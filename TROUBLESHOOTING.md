# RAHUUL RADAR — Troubleshooting Guide (v1.1)

---

## Common Issues & Verified Solutions

### 1. Paytm Money Authentication Errors (`TokenExpiredError` / HTTP 401)
* **Symptom:** API returns `TokenExpiredError: Paytm session token expired (HTTP 401)` or live order placement fails.
* **Root Cause:** Paytm Money public JWT access token has expired (Paytm access tokens expire daily after market hours).
* **Solution:**
  1. Login to Paytm Money Developer Portal.
  2. Generate a new request token / public JWT access token.
  3. Update `config.json` with the new token or submit via Desktop login dialog.
  4. Re-connect Paytm broker session.

---

### 2. WebSocket Stale Connection or Disconnects
* **Symptom:** Mobile or Desktop ticker prices stop updating.
* **Root Cause:** Network packet loss or silent socket drop by broker gateway.
* **Solution:**
  1. The integrated **WebSocket Watchdog (`PaytmWSWatchdog`)** automatically detects missing ticks (> 15s) and triggers socket auto-reconnect with exponential backoff (1s–60s).
  2. Verify network internet connectivity.
  3. Check `logs/paytm_websocket.log` to view reconnect latency and exact disconnect reason.

---

### 3. Pre-Trade Risk Engine Rejections (`RiskDecision.REJECTED`)
* **Symptom:** Order placement fails with message `"🔴 KILL SWITCH ACTIVE"` or `"Daily Loss Limit Breached"`.
* **Root Cause:** Order violates pre-trade risk safety parameters defined in `config.json`.
* **Solution:**
  * **Kill Switch Active:** Deactivate kill switch via Flutter Risk Screen toggle or `POST /api/v1/risk/kill-switch/deactivate`.
  * **Daily Loss Limit Hit:** Check daily realized P&L on Risk Screen. Daily loss threshold resets automatically at midnight.
  * **Max Open Trades Hit:** Close existing open positions before opening new trades.
  * **Duplicate Order Lock:** Wait for pending order to clear or release lock via Risk Screen.

---

### 4. SQLite Database Locks (`OperationalError: database is locked`)
* **Symptom:** Database write fails with database locked error.
* **Root Cause:** Concurrent file write lock in SQLite.
* **Solution:**
  1. All system databases utilize `PRAGMA journal_mode=WAL;` and 5,000ms busy timeouts.
  2. Ensure external SQLite viewing tools are opened in read-only mode.

---

### 5. Flutter App Unable to Connect to Backend (`Network error fetching portfolio`)
* **Symptom:** Mobile app shows network error or timeout.
* **Root Cause:** Incorrect IP/Port configured in Settings.
* **Solution:**
  1. Open Flutter app -> **Settings** tab.
  2. Ensure IP Address is set to server IP (`137.23.34.223`) and Port is set to `8000`.
  3. Tap **Save Settings** and pull to refresh.
