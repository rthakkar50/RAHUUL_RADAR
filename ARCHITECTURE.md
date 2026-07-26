# RAHUUL RADAR — System Architecture (v1.1)

## 1. System Overview

RAHUUL RADAR is an institutional-grade, multi-platform automated algorithmic trading scanner, risk management, and order execution platform. The system operates with a Python domain backend powering both a PyQt5 Desktop GUI and a Flutter Mobile client interface.

```
                  ┌──────────────────────────────┐
                  │    Flutter Mobile (Dart)     │
                  │ (Dashboard, Scanner, Risk,   │
                  │   Portfolio, Journal UI)     │
                  └──────────────┬───────────────┘
                                 │ HTTP REST
                                 ▼
┌─────────────────────────┐  ┌──────────────────────────────┐
│  Desktop PyQt5 (Python) │  │   FastAPI Backend (api/main) │
│ (Dashboard, Scanner, UI)│  │ (21 v1 REST Endpoints, 8000) │
└────────────┬────────────┘  └──────────────┬───────────────┘
             │ Direct Python                │
             └──────────────┬───────────────┘
                            ▼
┌───────────────────────────────────────────────────────────┐
│                    Core Domain Layer                      │
│ ┌──────────────────────┐   ┌────────────────────────────┐ │
│ │  Master Signal Pipe  │   │   Master AI Decision Engine│ │
│ └──────────┬───────────┘   └─────────────┬──────────────┘ │
│            │                             │                │
│ ┌──────────▼───────────┐   ┌─────────────▼──────────────┐ │
│ │ Live Risk Engine (M6)│   │ Paytm Order Engine (M5)    │ │
│ └──────────┬───────────┘   └─────────────┬──────────────┘ │
└────────────┼─────────────────────────────┼────────────────┘
             │                             │
             ▼                             ▼
┌─────────────────────────┐   ┌─────────────────────────────┐
│ Paytm Broker / Provider │   │ SQLite Databases (data/*.db)│
│ (OAuth, Live Orders)    │   │ (risk_state, audit, journal)│
└─────────────────────────┘   └─────────────────────────────┘
```

---

## 2. Component Architecture

### A. Core Engine Layer (`core/`)
* **Master Signal Pipeline (`master_signal_pipeline.py`):** Integrates technical sub-engines (Trend, Momentum, Structure, Volume, VWAP, ADX, MTF) into candidate signals.
* **Master AI Decision Engine (`master_ai_decision_engine.py`):** Scores trade setups (0–100) using institutional confidence calibration and false-breakout detection.
* **Live Risk Engine (`live_risk_engine.py`):** Mandatory pre-trade validation gate enforcing position sizing, daily loss/profit limits, exposure bounds, dedup locking, and kill switch protection.
* **Paytm Order Engine (`paytm_order_engine.py`):** Handles live Paytm REST order placement, margin calculations, brokerage previews, and SQLite audit logging.

### B. Scanner Subsystem (`scanner/`, `application/`)
* **Swing Scanner Service (`swing_scanner_service.py`):** Multi-threaded scanner running adaptive worker pools over Nifty 200 / F&O watchlists.
* **Intraday Engine (`strategy/intraday_engine.py`):** Detects VWAP breakouts, ORB patterns, and volume surges.
* **Option Chain Engine (`option_chain/`):** Evaluates PCR, IV skew, Max Pain, and synthetic option chains.

### C. Market Data Subsystem (`market/`, `broker/`)
* **Yahoo Provider (`market/yahoo_provider.py`):** Multi-timeframe OHLCV data fetcher with two-tier (in-memory + disk) caching.
* **Paytm Provider & Broker (`broker/paytm/paytm_broker.py`):** Institutional Paytm Money REST API client for account funds, positions, holdings, orders, and quotes.
* **Paytm WebSocket Watchdog (`market/paytm_websocket.py`):** Live tick stream manager featuring heartbeat monitoring (15s), stale timeout detection (15s), exponential backoff reconnect, and automatic subscription restoration.

### D. Applications & Interfaces (`ui/`, `mobile/`)
* **FastAPI Service (`api/main.py`):** Exposes 21 REST API endpoints on port 8000.
* **Desktop Application (`ui/`):** 76 PyQt5 files providing professional charting, scanner tables, position management, and settings controls.
* **Flutter Mobile App (`mobile/lib/`):** 6-tab production mobile app (Dashboard, Scanner, Portfolio, Journal, Risk, Settings).

---

## 3. End-to-End Data Flow

### Live Order Placement Flow
1. **User Action:** User taps **CONFIRM** on `OrderEntrySheet` in Flutter or `ProfessionalTradeWindow` in Desktop.
2. **API Request:** Flutter posts payload to `POST /api/v1/orders/execute`.
3. **Risk Gate:** `PaytmOrderEngine` invokes `LiveRiskEngine.validate_order()`.
   * Checks Kill Switch status.
   * Checks Auto-trading toggle.
   * Validates parameter bounds (Price > 0, Qty > 0).
   * Verifies Daily Loss Limit (-₹5,000) and Max Open Trades (5).
   * Computes approved position size (`PositionSizer`).
   * Verifies Portfolio Exposure (< 80%) & Sector Exposure (< 30%).
   * Locks dedup key (`SYMBOL-ACTION-QTY-PRICE`).
4. **Broker Execution:** If approved, `PaytmBroker.place_order()` transmits HTTPS request to Paytm Money REST API.
5. **Post-Execution:** `DailyRiskTracker` updates position state and releases dedup lock; audit trail is written to SQLite `data/order_audit_log.db`.
