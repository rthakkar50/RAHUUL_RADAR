# RAHUUL RADAR PRO - PRODUCTION OPERATIONS & MONITORING GUIDE

## 1. Overview
This operational manual outlines standard monitoring procedures, automated system health checks, and routine administrative workflows for RAHUUL RADAR PRO Version `1.0.0` in live production environments.

---

## 2. Monitoring Strategy & Health Checks

### 2.1 Application Health Checks
- **Memory & Process Monitoring**: Verify via system process managers (`htop`, Task Manager) or internal UI Diagnostics dialog that total memory consumption remains stable (< 500 MB typical baseline after aggressive pandas DataFrame garbage collection).
- **Thread & Deadlock Watchdog**: The System Orchestrator Engine (SOE) enforces a strict execution pipeline. If scanner UI worker threads exceed a 180-second execution window without emitting progress callbacks, terminate and respawn the worker process.

### 2.2 Telegram Health
- **Session Verification**: Daily ping using `/session` command via Telegram client. Ensure automated response returns active access token status and zero communication timeouts.
- **Deduplication & Retry Inspection**: Confirm Telegram automated alerting queue functions without rate-limit saturation (HTTP 429). Check sanitized production logs for graceful retry notices.

### 2.3 Paytm / Broker Connection Health
- **Token Validity Check**: Verify that `access_token` remains active prior to market open (09:00 AM IST). If tokens expire overnight, generate a fresh daily authentication link via `/login` command in Telegram or local broker authentication callbacks.
- **Option Chain Cache Health**: Monitor hit/miss ratios on the in-memory Option Chain cache (60-second TTL). Ensure cache purges execute cleanly during volatile market shifts.

### 2.4 Database Health
- **Integrity Inspection**: Periodically verify read/write access and WAL (Write-Ahead Logging) consistency across core SQLite data stores:
  - `radar.db` (Market signals and scanner snapshots)
  - `paper_trading.db` (Simulated execution ledger)
  - `trade_forensics.db` (AI decision scoring logs)
- **Lock Prevention**: Check logs for any concurrent SQLite database lock exceptions (`sqlite3.OperationalError: database is locked`). Ensure sequential database execution wrappers are observed.

### 2.5 Scanner Health
- **Latency Benchmark**: Active F&O universe scan cycles should complete under 15–30 seconds utilizing parallel threaded batch execution.
- **Symbol Resolution Rate**: Track occurrences of `NO_DATA` flags. A sudden surge in unparseable symbols (> 20% of universe) indicates upstream HTTP fallback provider rate-limiting or network proxy failure.

---

## 3. Routine Daily Operations Timeline (IST)

| Time (IST) | Phase | Operational Task |
| :--- | :--- | :--- |
| **08:45 AM** | Pre-Market Check | Validate network latency; check available disk space (> 500 MB). |
| **08:50 AM** | Broker Authentication | Issue `/login` via Telegram or run callback to refresh Paytm access tokens. |
| **09:15 AM** | Market Open | Verify WebSocket heartbeat and active F&O real-time streaming status on Dashboard. |
| **03:30 PM** | Market Close | Confirm completion of automated End-of-Day (EOD) Telegram Daily Summary alert. |
| **05:00 PM** | Post-Market Maintenance | Perform automated database backups and historical journal log rotation. |
