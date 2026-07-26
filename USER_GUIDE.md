# RAHUUL RADAR PRO - USER GUIDE (v1.0.0)

## 1. Overview
RAHUUL RADAR PRO is an institutional-grade algorithmic market data analytics, opportunity discovery, and portfolio monitoring platform designed for real-time decision support across equities and F&O markets.

## 2. Main Navigation & Modules

### 2.1 Dashboard
The Dashboard displays live market telemetry, AI summary scorecards, top BUY/SELL/WATCH signals, portfolio summary metrics, and system health status. If market data is unavailable, widgets cleanly reflect "No Data" with graceful offline state handling.

### 2.2 Scanner Engines
- **Swing Scanner**: Evaluates multi-timeframe structural breakouts and trend pullbacks (1D, 1W timeframes). Supports both Aggressive and Conservative mode filters.
- **Intraday Scanner**: Identifies momentum setups on 5m and 15m timeframes targeting precise profit milestones.
- **F&O / Active Scanner**: Real-time continuous analysis catching unusual volume spikes and option chain dynamics. Features an in-memory Option Chain cache (TTL = 60s) for lightning-fast responsiveness.

### 2.3 Portfolio & Trading Journal (Sprint 5 Architecture)
- **Portfolio Summary**: Displays Total Capital, Invested Amount, Available Cash, Current Portfolio Value, Today's P/L, Overall P/L, and Return %.
- **Open Positions & Closed Positions**: Comprehensive tabular view with real-time CMP updates and Risk-Reward tracking.
- **Performance Analytics**: Tracks Total Trades, Win Rate, Loss Rate, Average Winner/Loser, Profit Factor, and Largest Win/Loss.
- **Trading Journal**: Detailed log of completed trades with exit reason attribution and trade metrics.

### 2.4 Telegram Controller & Alerts (Sprint 6B Architecture)
Connects remotely via Telegram bot integration:
- **Commands**: 
  - `/login`: Generates a fresh daily Paytm login link and verifies session status.
  - `/session`: Reports detailed access token expiry, session validity, and reconnect counts.
- **Automated Alerts**: Real-time pushes for BUY, STRONG BUY, SELL, and HIGH RISK signals.
- **Daily Summary & Error Notifications**: Delivers automated end-of-day statistical summaries and critical connectivity error warnings.

## 3. Data Exports & Diagnostics
- **Export Options**: Export scanner output and journal logs cleanly to CSV, JSON, and Excel (.xlsx) formats.
- **System Diagnostics**: Built-in system health inspection verifying connection latency, memory stability, and API token validities.

## 4. FAQ
- **Q: How do I refresh expired broker sessions?**  
  A: Simply issue `/login` via your connected Telegram client or run authentication callback locally.
- **Q: Are sensitive access tokens stored or logged?**  
  A: No. v1.0.0 implements strict production-grade logging that sanitizes and obscures all tokens, API keys, and personal credentials.
