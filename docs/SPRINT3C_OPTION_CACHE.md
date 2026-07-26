# SPRINT 3C – Option Chain Cache Report
**Author:** Lead Software Architect, RAHUUL RADAR  
**Scope:** ONLY `market/paytm_provider.py` (Zero modifications to any other file)  
**Status:** Completed  

---

## Executive Summary
To eliminate repetitive high-latency REST option-chain fetches during real-time intraday F&O evaluations and scanner execution, an in-memory option chain caching layer has been integrated directly into `market/paytm_provider.py`. Operating under a strict 60-second Time-To-Live (TTL) rule and keyed by a composite `symbol + expiry` identifier, this caching architecture intercepts repeated requests for derivative contracts without altering API signatures, response parsing mechanics, or downstream business logic.

---

## Cache Design

### In-Memory Storage Structure
The cache utilizes an in-memory hash map attribute (`self._option_chain_cache`) initialized directly on the `PaytmMoneyProvider` class instance during instantiation:
```python
self._option_chain_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
```

### Composite Cache Key Mechanics
Each Option Chain request targeting Paytm Money Open APIs can be queried with or without an explicit expiry date parameter. To prevent data collisions across weekly and monthly derivative contracts, cache entries are indexed using a strict composite key format:
$$\text{cache\_key} = \text{symbol} + \text{"\_"} + \text{str(expiry)}$$
Examples:
* `"RELIANCE.NS_None"` (Default option chain request across all near active series)
* `"BANKNIFTY_2026-07-30"` (Specific weekly expiration series)
* `"NIFTY_2026-08-27"` (Monthly settlement contract series)

### Intercept Flow
When `get_option_chain(symbol, expiry)` is called:
1. **Connection Readiness:** Validates connection state (`if not self.is_connected(): raise ConnectionError(...)`).
2. **Cache Verification:** Generates the composite key and queries `self._option_chain_cache`.
3. **Instant Servicing on Hit:** If an unexpired entry exists, it logs a debug notice and immediately returns the cached dictionary object without performing network IO.
4. **Transparent Update on Miss:** If missing or expired, a fresh REST GET query executes against `/data/fno/v1/option-chain`. Upon receiving a successful `200 OK` JSON response, the tuple `(time.time(), data)` is stored in `_option_chain_cache` before being returned.

---

## TTL Strategy

### 60-Second Eviction Rule
Derivative pricing, Open Interest (OI) buildup, and Max Pain distributions update dynamically throughout trading sessions, yet scanner loops evaluating multi-condition intraday setups frequently re-query option metrics across dozens of algorithms within seconds. To balance quote precision with network reduction, a strict **60.0 second TTL** constant was implemented:
```python
OPTION_CHAIN_CACHE_TTL = 60.0
```

### Expiry Verification Logic
Upon intercepting a cache key match, the provider computes the delta between current operating system execution time (`time.time()`) and the recorded entry timestamp:
```python
if time.time() - timestamp < self.OPTION_CHAIN_CACHE_TTL:
    return cached_data
```
If the delta equals or exceeds 60 seconds, the stale cache entry is ignored, and execution seamlessly proceeds to fetch a fresh JSON option chain payload from the broker server, automatically overwriting the outdated cache tuple upon completion.

---

## Validation

### 1. Zero Architectural and Structural Drift
* [x] **No Business Logic Changes:** F&O summary calculations (`get_fno_summary`), option strike extractions, and mathematical derivations across intraday scanner services remain completely unmodified.
* [x] **No Parser Changes:** Raw JSON payload processing (`response.json()`) is cached verbatim and served identically to live API responses.
* [x] **No API Signature Drift:** Public method declarations (`get_option_chain(self, symbol: str, expiry: str = None) -> Dict[str, Any]`) remain 100% backward compatible.
* [x] **Single-File Isolation:** Confirmed zero modifications outside `market/paytm_provider.py`.

### 2. Runtime Behavior Verification
An inline execution test suite was run inside `.venv/bin/python3` verifying caching behaviors:
1. **Cache Miss Ingestion:** Initial call to `get_option_chain("RELIANCE.NS", "2026-07-30")` triggered exactly `1` network HTTP request to mock Paytm servers and recorded the payload in `_option_chain_cache`.
2. **Instant Cache Hit Service:** A consecutive call to the exact same contract within the 60-second window returned the exact cached response instantly with zero additional network executions (HTTP request count remained at `1`).
3. **Automated Eviction & Refresh:** Advancing the entry timestamp by $>60$ seconds confirmed immediate expiration recognition, cleanly executing a fresh API fetch (HTTP request count incremented to `2`).
4. **Result:** `✔ Option Chain Cache Validation Passed`

---

## Rollback Plan
If production diagnosis requires bypassing option chain memoization (for instance, during high-frequency tick arbitrage debugging where option chain state must be pulled live on every single millisecond eval), execute the following revert protocol:

1. **Remove Class Attribute and TTL Constant:**
   In `market/paytm_provider.py`, strip `OPTION_CHAIN_CACHE_TTL = 60.0` from the class attributes and delete `self._option_chain_cache = {}` from `__init__`.
2. **Remove Intercept Gate from `get_option_chain`:**
   Delete the cache check block immediately following `is_connected()` validation:
   ```python
   # Delete these lines in get_option_chain():
   cache_key = f"{symbol}_{expiry}"
   if cache_key in self._option_chain_cache:
       timestamp, cached_data = self._option_chain_cache[cache_key]
       if time.time() - timestamp < self.OPTION_CHAIN_CACHE_TTL:
           self.logger.debug(...)
           return cached_data
   ```
3. **Remove Storage Trigger:**
   Change the return block back to direct JSON output without tuple persistence:
   ```python
   # Revert this:
   data = response.json()
   self._option_chain_cache[cache_key] = (time.time(), data)
   return data
   
   # Back to original:
   return response.json()
   ```
4. **Git Quick Reset:**
   Alternatively, perform an atomic Git file restoration:
   ```bash
   git checkout -- market/paytm_provider.py
   ```

---
*Report sealed and verified by Lead Software Architect for RAHUUL RADAR.*
