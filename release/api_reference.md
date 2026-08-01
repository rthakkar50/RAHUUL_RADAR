# RAHUUL_RADAR Enterprise v2.0 — API Reference

Official REST API reference documentation for RAHUUL_RADAR Enterprise v2.0.

---

## Base URL

- **Production Cloud:** `https://rahuul-radar.onrender.com`
- **Local Dev:** `http://localhost:8000`

---

## Endpoints

### 1. `GET /api/v1/health`
- **Description:** System health check endpoint.
- **Headers:** None required.
- **Response `200 OK`:**
```json
{
  "status": "HEALTHY",
  "version": "RAHUUL_RADAR v2.0",
  "timestamp": "2026-08-01T14:20:00Z"
}
```

### 2. `GET /api/v1/dashboard/home`
- **Description:** Returns Mobile Dashboard Home payload (Market Status, Account Status, Active Trades).
- **Response `200 OK`:**
```json
{
  "market_status": { "regime": "Bull Trend", "nifty": 24500.0, "vix": 12.8 },
  "account_status": { "equity": 1000000.0, "todays_pnl": 15000.0, "buying_power": 5000000.0 },
  "open_trades_count": 3
}
```

### 3. `GET /api/v1/fno/chain`
- **Query Params:** `symbol` (e.g. `NIFTY`, `BANKNIFTY`, `RELIANCE`), `expiry` (optional).
- **Response `200 OK`:**
```json
{
  "symbol": "NIFTY",
  "spot_price": 24500.0,
  "pcr": 1.15,
  "max_pain": 24500.0,
  "atm_iv": 13.5
}
```

### 4. `POST /api/v1/paper/order`
- **Description:** Places a virtual paper order.
- **Body `JSON`:**
```json
{
  "symbol": "RELIANCE",
  "action": "BUY",
  "order_type": "MARKET",
  "quantity": 10,
  "price": 2980.0,
  "stop_loss": 2920.0,
  "target_1": 3050.0
}
```

### 5. `GET /api/v1/ops/metrics`
- **Description:** SRE Performance metrics endpoint.
- **Response `200 OK`:**
```json
{
  "ai_latency_ms": 2.1,
  "fno_latency_ms": 1.8,
  "memory_mb": 85.5,
  "cpu_pct": 4.2
}
```
