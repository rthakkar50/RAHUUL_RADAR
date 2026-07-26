# RAHUUL RADAR — Changelog

All notable changes to the RAHUUL RADAR trading system are documented in this file.

---

## [v1.1.0] - 2026-07-26

### Added
* System documentation suite: `ARCHITECTURE.md`, `API.md`, `DATABASE.md`, `DEPLOYMENT.md`, `TROUBLESHOOTING.md`.

---

## [v1.0.1] - 2026-07-26

### Maintenance & Code Cleanup
* Removed 45 dead code files, `.bak` files, and obsolete root scratch scripts (`master_signal_pipeline.py.bak`, `backtest_orchestrator.py.bak`, duplicate provider files).
* Cleaned up root directory while maintaining 100% test suite compatibility (40/40 tests passing).

---

## [v1.0.0-rc1] - 2026-07-26

### Added
* **Sprint M6: Production Live Risk Engine**
  * Integrated `LiveRiskEngine` as mandatory pre-trade validation gate.
  * Position sizing (Fixed Quantity, Fixed Capital, Risk %, ATR-based, Max Exposure).
  * Daily Loss Limit (-₹5,000), Profit Target (₹15,000), Consecutive Losses (3), Max Open Trades (5), Max Orders/Day (20).
  * Portfolio Exposure (80%) and Sector Exposure (30%) limits.
  * Duplicate order locking (`DailyRiskTracker.lock_order`).
  * Emergency Kill Switch & Auto-trading toggles.
  * Risk endpoints: `/api/v1/risk/report`, `/validate`, `/kill-switch/activate`, `/kill-switch/deactivate`, `/auto-trading/disable`, `/auto-trading/enable`.
* **Sprint FC1: Flutter Trade Journal & Analytics Screen**
  * Production mobile Journal screen UI (`journal_screen.dart`).
  * Performance Metrics (Total Trades, Win Rate %, Profit Factor, Avg Hold Time).
  * Daily P&L and Monthly P&L Overview cards.
  * Filter chips (ALL, BUY, SELL, WIN, LOSS).
  * Detailed trade cards (Symbol, BUY/SELL badge, Entry, Exit, Qty, P&L, P&L %, R-Multiple, AI Score, Confidence, Trade Date).
  * Models (`journal_model.dart`) and Repository (`journal_repository.dart`).
* **Sprint M4.7: Paytm WebSocket Watchdog**
  * Production-grade WebSocket Watchdog (`PaytmWSWatchdog`) in `market/paytm_websocket.py`.
  * Heartbeat monitoring (15s ping interval / 5s timeout) with pong latency tracking.
  * Stale connection detection (15.0s timeout).
  * Exponential backoff reconnect loop (1s to 60s max).
  * Duplicate session prevention via `_connecting_lock`.
  * Automatic subscription restoration on socket reconnect.
  * Reconnect reason & latency logging (ms accuracy).
  * Thread teardown routines to prevent memory leaks or orphan daemon threads.

### Fixed
* Fixed pre-trade risk gate zero/negative price/quantity validation bug (`live_risk_engine.py`).
* Fixed potential `AttributeError` crash on null Paytm API responses (`paytm_broker.py`).
* Fixed Flutter Dart compilation errors in `journal_screen.dart` and `risk_screen.dart`.

---

## [v1.0.0] - 2026-07-25

### Initial Release
* Initial release of RAHUUL RADAR PRO desktop & mobile algorithmic trading suite.
* Multi-layer scanner engine, Paytm Money broker integration, PyQt5 desktop suite, paper trading engine, SQLite data persistence.
