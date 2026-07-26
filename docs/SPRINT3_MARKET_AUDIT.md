# SPRINT 3A: MARKET DATA ARCHITECTURE AUDIT REPORT
**Author:** Lead Software Architect, RAHUUL RADAR  
**Status:** AUDIT ONLY (Zero Source Code Modifications)  
**Target:** Production Architecture Readiness (Version 1.0)  

---

## 1. Executive Summary
This report provides an exhaustive architectural audit of the market data ingestion, transmission, caching, and dependency structures across the RAHUUL RADAR trading platform. The investigation audited five core subsystem modules: `market/`, `broker/paytm/`, `application/`, `api/`, and `core/`. 

The core findings confirm a functional hybrid architecture: **Paytm Money Open APIs** serve as the primary institutional gateway for real-time live pricing, quote broadcasting (WebSocket), and F&O Option Chain metrics, while **Yahoo Finance** acts as the deep historical OHLCV data engine and secondary fallback provider. While the WebSocket layer exhibits robust self-healing capability (exponential backoff, ping/pong monitors, and heartbeat timeout recovery), several latency bottlenecks and vulnerability vectors were uncovered in the REST fallback mechanics—primarily missing network timeout parameters on live price endpoints, synchronous single-threaded evaluation loops in scanner services, and uncached repetitive option-chain queries during F&O evaluations.

---

## 2. Architecture Diagram (ASCII)

```
===========================================================================================================
                                   RAHUUL RADAR MARKET DATA Flow Architecture
===========================================================================================================

       [ Paytm Money Developer APIs ]                            [ Yahoo Finance API / yfinance ]
          /                 \                                                   |
         / (WSS Live Stream) \ (REST Option Chains & Live Quotes)               | (REST Historical OHLCV)
        v                     v                                                 v
+------------------+  +-------------------------------+              +------------------------------------+
| PaytmLiveBroadcast| |       PaytmMoneyProvider       |              |        YahooFinanceProvider        |
|  (WebSocket L1)  | |        (Provider L2)          |              |           (Provider L3)            |
+------------------+  +-------------------------------+              +------------------------------------+
     |                        |                                                 |
     | [tick_cache & vol_cache]| [Bulk _rest_cache (40-symbol chunks)]            | [Memory _cache (15m TTL) & Disk .pkl]
     \------------------------+-------------------------------------------------+
                              |
                              v
                +----------------------------+
                |     MarketDataManager      |  <--- (Central Unified Data Routing & Fallback Controller)
                +----------------------------+
                              |
       +----------------------+----------------------+
       |                                             |
       v (Historical Candles & Indicators)           v (Live LTP, Volume, & Option Chains / F&O Summary)
+-----------------------------------+   +-------------------------------------------------------------+
|    Core Algorithmic Engines       |   |             Application Scanner Services                    |
|  -------------------------------  |   |  ---------------------------------------------------------  |
|  • TrendEngine                    |   |  • SwingScannerService.execute_swing_scan()                 |
|  • MomentumEngine                 |   |  • IntradayScannerService.execute_intraday_scan()           |
|  • StructureEngine                |   |    ├── FNOFilterEngine (Strict OI, PCR & Liquidity Gates)   |
|  • RelativeStrengthEngine         |   |    ├── InstitutionalValidationEngine                        |
|  • SectorRotationEngine           |   |    └── TradeExecutionCenter                                 |
|  • AdaptiveStrategyEngine         |   +-------------------------------------------------------------+
|  • MasterAIDecisionEngine         |                  |
+-----------------------------------+                  | (Aggregated Signals & Trade Setups)
               |                                       v
               |                             +----------------------------+
               +---------------------------> |         api/main.py        |  <--- (FastAPI Gateway & Cache L4)
                     (Pipeline Score)        |  [_SCANNER_CACHE (3m TTL)] |
                                             +----------------------------+
                                                       |
                                                       v
                                            [ Mobile App UI / Web UI / GTK ]
===========================================================================================================
```

---

## 3. Current Data Flow

### 1. Market Data Entry Flow
Live market data enters the application through three primary ingest vectors:
* **Live Tick & Volume WebSocket:** Real-time data streams into `market/paytm_websocket.py` via the endpoint `wss://developer-ws.paytmmoney.com/broadcast/user/v1/data?x_jwt_token={token}`.
* **REST Live Prices & Option Chains:** Supplemental live quotes and derivative option chains enter via `market/paytm_provider.py` querying `https://developer.paytmmoney.com/data/v1/price/live` (`mode=LTP` or `mode=QUOTE`) and `https://developer.paytmmoney.com/data/fno/v1/option-chain`.
* **REST Historical Candletick Feed:** Historical OHLCV arrays enter through `market/yahoo_provider.py` utilizing multi-threaded HTTP chunking via the `yfinance` adapter, supplemented by persistent local caching.

### 2. Complete End-to-End Data Flow
1. **From Broker:** Market quotes originate at Paytm Money Open APIs and Yahoo Finance endpoints.
2. **To Provider:** `PaytmMoneyProvider` and `YahooFinanceProvider` absorb raw payloads, normalizing JSON responses and dataframes into unified `OHLCV` dataclass objects and price primitives.
3. **To Parser & Cache:** WebSocket binary/text frames are decoded in `PaytmLiveBroadcast._on_message()`, immediately updating `tick_cache` and `vol_cache`. REST calls populate L2 (`_rest_cache`) and L3 (`YahooFinanceProvider._cache` memory and disk pickle).
4. **To Scanner:** `MarketDataManager` orchestrates distribution. Application scanner services (`SwingScannerService`, `IntradayScannerService`) fetch symbol universes (`get_all_symbols()`) and invoke `ScannerEngine.scan_market()`.
5. **To UI / API Gateway:** Scanner results are processed through `MasterSignalPipeline`, cached in `api/main.py` (`_SCANNER_CACHE` with a 180-second TTL via non-blocking daemon threads), and delivered instantly as JSON payloads to external mobile and UI clients.

---

## 4. WebSocket Lifecycle Analysis
The live streaming architecture in `market/paytm_websocket.py` (`PaytmLiveBroadcast`) is structured around a resilient, self-healing singleton:
* **Connection:** Triggered via `connect()`, spawning a background daemon thread (`ws_thread`) that instantiates a `websocket.WebSocketApp` configured with automated event handlers (`on_open`, `on_message`, `on_error`, `on_close`, `on_pong`).
* **Authentication:** Authorizes on connection handshake using the OAuth public access token injected into the wss query parameter.
* **Heartbeat & Liveness Monitoring:** The socket runs with `ping_interval=30` and `ping_timeout=10`. A separate supervisor daemon thread (`_start_heartbeat_monitor`) checks every 5 seconds if `time.time() - self.last_msg_time > 45`. If no messages or pong heartbeats arrive within 45 seconds, it forcefully closes the dead socket to trigger clean re-establishment.
* **Reconnect Mechanics:** Auto-reconnection operates inside an exponential backoff loop (`backoff = min(backoff * 2, 60)` starting at 1 second up to 60 seconds). Upon successful reconnect (`_on_open`), it automatically re-transmits `"SUBSCRIBE"` payloads for all instruments recorded in `subscribed_instruments`.
* **Failure & Exhaustion Handling:** To protect against token expiry lockouts, if disconnection coincides with backoff $\ge 16$ seconds, it tracks consecutive authentication failures. Upon reaching 5 consecutive auth failures, it halts further attempts (`_should_reconnect = False`) and triggers logger alerts requiring token renewal.

---

## 5. REST Fallback Dynamics
When live real-time quotes cannot be fulfilled via the WebSocket cache (a cache miss), the system gracefully downgrades to REST endpoints:
* **Target APIs & Call Frequency:** `MarketDataManager.get_live_price()` and `get_live_quote()` increment `rest_fallback_count` and invoke `PaytmMoneyProvider.get_last_price()`, which sends HTTP GET requests to `https://developer.paytmmoney.com/data/v1/price/live`. If Paytm Money returns empty data or errors, it delegates to `YahooFinanceProvider.get_last_price()`.
* **Sequential vs. Parallel Execution:**
  * *Pre-caching Phase (Parallel):* During initialization, `pre_cache()` bulk-fetches quotes. In `PaytmMoneyProvider.pre_cache()`, requests are aggregated in chunks of 40 symbols per HTTP request (`mode=QUOTE`). In `YahooFinanceProvider.pre_cache()`, historical data downloads run in multithreaded worker pools (`ThreadPoolExecutor(max_workers=4)` with `threads=True`).
  * *Scanner Evaluation Loop (Sequential):* During real-time intraday and swing scan execution, symbol evaluation runs inside synchronous, single-threaded iterations. If a symbol misses the cache, fallback REST calls and option chain fetches (`get_fno_summary()`) are executed sequentially, blocking thread execution until network I/O completes.

---

## 6. Scanner Dependency Graph
The following matrix details the strict dependencies of application scanners and decision engines on underlying market data types:

| Module / Engine | Primary Data Dependency | Ingest Route / Provider | Fallback Provider |
| :--- | :--- | :--- | :--- |
| **TrendEngine** | OHLCV Candles (Daily, 5m, 15m, 1h) | `MarketDataManager.get_history()` $\rightarrow$ Yahoo | Local Pickle Cache |
| **MomentumEngine** | OHLCV Volume & Price Series | `MarketDataManager.get_history()` $\rightarrow$ Yahoo | Local Pickle Cache |
| **StructureEngine** | Swing High/Low OHLCV Arrays | `MarketDataManager.get_history()` $\rightarrow$ Yahoo | Local Pickle Cache |
| **RelativeStrengthEngine** | Benchmark Index vs. Stock OHLCV | `MarketDataManager.get_history()` $\rightarrow$ Yahoo | Local Pickle Cache |
| **SectorRotationEngine** | Multi-symbol Sector ETF/Stock Prices | `MarketDataManager.get_history()` $\rightarrow$ Yahoo | Local Pickle Cache |
| **MarketEngine** | Index NIFTY/BANKNIFTY OHLCV & Ticks | `MarketDataManager.get_history()` $\rightarrow$ Yahoo | Local Pickle Cache |
| **FNOFilterEngine** | Option Chain (OI, PCR, Max Pain, Volume) | `PaytmMoneyProvider.get_fno_summary()` | Default Zero Summary |
| **IntradayScannerService** | Real-time LTP, Live Volume, F&O OI | `MarketDataManager.get_live_quote()` + WebSocket | Paytm REST $\rightarrow$ Yahoo |
| **SwingScannerService** | Daily OHLCV & Closing LTP | `MarketDataManager.get_history()` & Live Price | Paytm REST $\rightarrow$ Yahoo |

---

## 7. Caching Architecture
The platform operates a 4-tier hierarchical caching structure to minimize latency and network overhead:
1. **L1 Real-Time Tick Cache (`PaytmLiveBroadcast`):** In-memory dictionaries (`tick_cache[security_id]` and `vol_cache[security_id]`) updated sub-second via WebSocket broadcasts. Tracks live telemetry for hit and miss rates.
2. **L2 Bulk REST Pre-Cache (`PaytmMoneyProvider._rest_cache`):** In-memory dictionary populated during initial scanner boot in chunks of 40 equities/indices, shielding the broker from excessive per-symbol fallback calls.
3. **L3 Historical Data Cache (`YahooFinanceProvider._cache` & Disk Pickle):** In-memory OHLCV storage guarded by threading locks with a 15-minute Time-to-Live (TTL). Backed asynchronously to local disk (`~/.cache/rahuul_radar/yahoo_cache.pkl`) to survive application restarts.
4. **L4 API Response Gateway Cache (`api/main.py` `_SCANNER_CACHE`):** Thread-safe JSON result cache at the FastAPI layer. Maintains a 180-second TTL; when expired, queries return instantly from stale memory while silently spawning a daemon thread (`_run_background_scan`) to update results without client timeout errors.

---

## 8. Risk Analysis & Vulnerabilities
1. **Missing HTTP Timeouts in Paytm REST Provider (HIGH RISK):** In `market/paytm_provider.py`, HTTP GET network executions in `get_last_price()` (line 203), `get_volume()` (line 334), `get_option_chain()` (line 372), and `pre_cache()` (line 286) invoke `requests.get()` **without explicit `timeout` arguments**. If the broker API experiences packet dropping or server latency, these threads will hang indefinitely, freezing scanner evaluations and API endpoints.
2. **Rate-Limit Vulnerabilities during Fallback Spikes:** If the WebSocket connection disconnects during an active trading window and token recovery fails, scanners evaluating 200+ symbols will execute sequential fallback HTTP REST queries. Without token buckets, rate-limit backoff, or circuit breakers, this risks triggering HTTP 429 (Too Many Requests) errors and automated account API IP blocklists.
3. **Uncached Option Chain Queries in F&O Scanners:** In `intraday_scanner_service.py`, evaluating options strategies invokes `paytm_provider.get_fno_summary(symbol)`, which triggers a fresh REST fetch to `fno/v1/option-chain` per symbol without local caching. Scanning 150 F&O instruments triggers 150 immediate, unbuffered HTTP requests.
4. **Token Refresh Race Conditions:** When `PaytmMoneyProvider` receives an HTTP 401 response during REST invocation, it calls `_refresh_token()`. In multi-threaded worker deployments, simultaneous 401 errors across distinct threads can cause redundant, overlapping authentication requests that destabilize OAuth state.

---

## 9. Performance Bottlenecks
1. **Synchronous Single-Threaded Scanner Loops:** While initial data pre-caching runs concurrently via `ThreadPoolExecutor`, the downstream signal evaluation loops in `IntradayScannerService` and `SwingScannerService` process symbols sequentially in Python. When IO fallbacks occur during the loop, execution time degrades linearly ($O(N)$).
2. **Unbuffered Option Chain Payload Decoding:** Option chain JSON responses from Paytm Money contain comprehensive call/put arrays across all strike prices. Parsing and computing Open Interest (OI) changes, PCR ratios, and Max Pain on every scanner iteration without short-term memoization consumes excessive CPU cycles.
3. **Redundant DataFrame Conversions:** Inner wrappers such as `SectorEngineDataProviderWrapper` continuously translate custom `OHLCV` objects into Pandas `DataFrames` inside scan loops, generating unnecessary Python garbage collection overhead and memory fragmentation.

---

## 10. Technical Debt Inventory (Files with Highest Debt)

| File Path | Lines | Key Technical Debt Items Identified |
| :--- | :--- | :--- |
| `market/paytm_provider.py` | 462 | Missing HTTP network timeout parameters on REST calls; absence of circuit-breaker patterns; repetitive token refresh boilerplate across method blocks. |
| `application/intraday_scanner_service.py` | 633 | Exceeds 500 lines; tight coupling between F&O filtering (`FNOFilterEngine`), trade locks, validation, and scanner orchestration; sequential execution loops. |
| `application/swing_scanner_service.py` | 631 | Exceeds 500 lines; significant duplication of provider instantiation, universe resolution, and pre-cache setup logic shared with Intraday scanner. |
| `core/master_signal_pipeline.py` | 600+ | Large engine pipeline file with lingering repository debris (`master_signal_pipeline.py.bak` backup file stored alongside active code). |
| `market/yahoo_provider.py` | 360 | Complex mixed memory/disk synchronization state; thread-safe lock contention under high concurrent scanner requests. |

---

## 11. Recommended Optimisation Order (Highest ROI First)
To transition RAHUUL RADAR to a robust Version 1.0 commercial production release, optimizations must be addressed in strict order of architecture impact and risk mitigation:

1. **Rank 1: Inject Explicit HTTP Timeouts in Provider REST Executions (Critical Reliability)**  
   * *Action:* Add mandatory explicit timeout rules (e.g., `timeout=3.0` or `timeout=(3.0, 5.0)`) across all `requests.get` and `requests.post` invocations in `market/paytm_provider.py` to prevent network thread lockups.
2. **Rank 2: Implement Option Chain Memory Caching & Memoization (High Performance / Low Effort)**  
   * *Action:* Implement a lightweight 60-second TTL in-memory cache inside `PaytmMoneyProvider.get_option_chain()` / `get_fno_summary()`. This instantly drops intraday F&O scan HTTP payload traffic by up to 95%.
3. **Rank 3: Integrate Circuit Breaker & Fallback Backpressure Protection (System Resilience)**  
   * *Action:* Equip `MarketDataManager` and provider REST fallbacks with a fast-fail circuit breaker. Upon consecutive API timeouts or HTTP 429 rate limits, open the circuit and route immediately to local cache or fallback providers without waiting for network timeouts.
4. **Rank 4: Parallelize Symbol Evaluation Loops in Scanner Services (Throughput Scaling)**  
   * *Action:* Transition the sequential per-symbol evaluation loops in `intraday_scanner_service.py` and `swing_scanner_service.py` into thread-pool or process-pool worker execution architectures, leveraging pre-cached multi-core processing.
5. **Rank 5: Extract Unified Base Scanner & Provider Setup Service (Technical Debt & DRY Cleanup)**  
   * *Action:* Refactor duplicate provider initializations, symbol universe filtering, and data provider DataFrame conversion wrappers out of individual scanner services into a centralized `BaseScannerService` superclass.
6. **Rank 6: Repository Sanitization & Legacy Code Purge (Codebase Hygiene)**  
   * *Action:* Remove obsolete repository artifacts including `core/master_signal_pipeline.py.bak` and streamline redundant exception loggers across provider interfaces.

---
*Audit completed by Lead Software Architect in strict compliance with Sprint 3A governance guidelines.*
