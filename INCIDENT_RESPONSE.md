# RAHUUL RADAR PRO - INCIDENT RESPONSE & TRIAGE RUNBOOKS

## 1. Overview
This emergency incident response guide defines standardized triage protocols and remediation runbooks for critical infrastructure anomalies and service disruption events in RAHUUL RADAR PRO Version `1.0.0`.

---

## 2. Incident Severity Classifications
- **SEV-1 (Critical Blocking)**: Total system halt, database corruption, or complete loss of live market data streaming during active market trading hours (09:15–15:30 IST).
- **SEV-2 (Degraded Performance)**: Fallback provider rate-limiting, temporary WebSocket reconnection looping, or delayed Telegram alert delivery.
- **SEV-3 (Non-Impact Defect)**: Isolated symbol delisting failures, GUI rendering lag, or background log rotation warnings.

---

## 3. Standard Operating Runbooks

### Runbook 1: Scanner Failure (SEV-1 / SEV-2)
- **Symptom**: Scanner execution progress freezes at 0% or crashes mid-batch; system outputs `TimeoutException` or HTTP rate-limit errors in `/logs`.
- **Diagnosis**: 
  1. Inspect network connectivity and confirm DNS resolution to target market providers (Dhan / Yahoo Finance).
  2. Check sanitized application logs for repeated HTTP 429 (Too Many Requests) throttle notices.
- **Remediation**:
  1. **Abort Active Thread**: Click `Abort Scan` in the UI to safely signal thread-pool shutdown and release UI mutex locks.
  2. **Purge Cache & Throttle**: Delete temporary tick stores inside `/cache/` and wait for a 3-minute mandatory cooldown period.
  3. **Provider Failover**: Open `Settings` dialog and switch active `Data Provider` from Yahoo Finance fallback to authenticated Dhan broker endpoint (or vice versa).

### Runbook 2: Broker Login Failure (SEV-1)
- **Symptom**: Authentication callback errors on startup; access tokens rejected with HTTP 401/403 status; live Option Chain pulls return empty structures.
- **Diagnosis**: 
  1. Verify token expiration timestamp in sanitized log outputs (Paytm / Dhan OAuth tokens expire daily).
  2. Ensure `api_key` and `api_secret_key` remain correctly mapped inside `config.json`.
- **Remediation**:
  1. **Trigger Remote Re-auth**: Issue `/login` via connected Telegram client or execute interactive authentication callback locally.
  2. **Token Refresh Validation**: Confirm generation of fresh `access_token` and verify successful session check response via `/session`.

### Runbook 3: WebSocket Disconnect & Heartbeat Loss (SEV-2)
- **Symptom**: Live streaming prices freeze on Active Scanner and Dashboard; log records explicit WebSocket socket drop or missed ping/heartbeat.
- **Diagnosis**: 
  1. Inspect upstream broker API health status and local network firewall rules for socket termination.
  2. Confirm auto-reconnect retry counter has not exceeded maximum consecutive retries (Max = 5).
- **Remediation**:
  1. **Automated Reconnect**: Allow built-in exponentional backoff reconnect logic to re-establish authenticated websocket bind.
  2. **Manual Intervention**: If reconnect limit is exceeded, execute a clean application daemon restart (`python3 main.py` or systemd service restart) to re-initiate websocket handshaking.

### Runbook 4: Database Lock & Transaction Contention (SEV-1)
- **Symptom**: Database write operations error with `sqlite3.OperationalError: database is locked`; paper trade positions or journal entries fail to persist.
- **Diagnosis**: 
  1. Determine if external programs (e.g., SQLite DB Browser or Excel export lock) hold active write handles on `radar.db` or `paper_trading.db`.
  2. Verify that thread-safe sequential DB connections are functioning within the System Orchestrator Engine.
- **Remediation**:
  1. **Release External Handles**: Terminate third-party inspection utilities locking local database `.sqlite` or `.db` files.
  2. **WAL Checkpoint**: Perform an emergency manual write-ahead logging checkpoint:
     ```bash
     sqlite3 radar.db "PRAGMA wal_checkpoint(TRUNCATE);"
     ```
  3. If database structural corruption is detected, revert to the latest verified daily online backup from `/backups/db/`.

### Runbook 5: Telegram Controller Failure (SEV-2 / SEV-3)
- **Symptom**: Automated scanner BUY/SELL alerts or daily summary reports fail to deliver to configured Telegram channel; polling listener halts.
- **Diagnosis**: 
  1. Verify internet connectivity to Telegram Bot API HTTPS endpoints (`api.telegram.org:443`).
  2. Check sanitized logs for authentication token revocation or bot chat permissions revocation.
- **Remediation**:
  1. Confirm Telegram Bot API key validity in system settings.
  2. Rely on automated messaging reliability and deduplication queues; the system will gracefully buffer notifications during transient unreachable network windows and retry upon connectivity restoration.
