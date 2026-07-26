# RAHUUL RADAR — REST API Specification (v1.1)

Base URL: `http://137.23.34.223:8000/api/v1`

---

## Endpoints Summary

| Method | Endpoint Path | Summary | Tags |
|---|---|---|---|
| `GET` | `/health` | Application health check | Health |
| `GET` | `/scanner/swing` | Fetch active swing scanner signals | Scanner |
| `GET` | `/portfolio` | Fetch portfolio summary & open positions | Portfolio |
| `GET` | `/journal` | Fetch trade journal history & analytics | Journal |
| `POST` | `/orders/preview` | Preview margin, brokerage & total cost | Orders |
| `POST` | `/orders/execute` | Execute live order via Paytm Money | Orders |
| `GET` | `/orders/book` | Fetch live Paytm order book | Orders |
| `POST` | `/orders/cancel/{id}` | Cancel live Paytm order | Orders |
| `GET` | `/orders/audit-log` | Fetch SQLite order audit trail | Orders |
| `GET` | `/risk/report` | Fetch risk budget & exposure report | Risk |
| `POST` | `/risk/validate` | Pre-trade risk validation gate | Risk |
| `POST` | `/risk/kill-switch/activate` | Activate Emergency Kill Switch | Risk |
| `POST` | `/risk/kill-switch/deactivate` | Deactivate Kill Switch | Risk |
| `POST` | `/risk/auto-trading/disable` | Disable automated orders | Risk |
| `POST` | `/risk/auto-trading/enable` | Enable automated orders | Risk |
| `GET` | `/risk/state` | Raw daily risk state snapshot | Risk |

---

## Endpoint Details & Request/Response Examples

### 1. Health Check
* **`GET /api/v1/health`**
* **Response (200 OK):**
```json
{
  "status": "online",
  "environment": "production",
  "market_status": "OPEN",
  "timestamp": 1785085670.0
}
```

---

### 2. Swing Scanner Signals
* **`GET /api/v1/scanner/swing`**
* **Response (200 OK):**
```json
{
  "results": [
    {
      "symbol": "RELIANCE",
      "signal": "BUY",
      "entry_price": 2450.0,
      "sl": 2400.0,
      "target": 2550.0,
      "score": 88.5,
      "confidence": 91.5,
      "reason": "Breakout confirmed above resistance"
    }
  ],
  "exec_time": 4.2
}
```

---

### 3. Portfolio Summary
* **`GET /api/v1/portfolio`**
* **Response (200 OK):**
```json
{
  "portfolio_value": 1028400.0,
  "today_pnl": 3500.0,
  "overall_pnl": 28400.0,
  "available_cash": 750000.0,
  "margin_used": 150000.0,
  "buying_power": 3000000.0,
  "positions": [
    {
      "symbol": "INFY",
      "qty": 10,
      "avg_price": 1500.0,
      "current_price": 1535.0,
      "pnl": 350.0,
      "return_pct": 2.33
    }
  ]
}
```

---

### 4. Trade Journal & Analytics
* **`GET /api/v1/journal?limit=100`**
* **Response (200 OK):**
```json
{
  "trades": [
    {
      "id": "TRADE-101",
      "symbol": "RELIANCE",
      "signal": "BUY",
      "entry_price": 2450.0,
      "exit_price": 2520.0,
      "qty": 50,
      "pnl": 3500.0,
      "r_multiple": "+1.4R",
      "result": "WIN",
      "trade_date": "2026-07-24"
    }
  ],
  "analytics": {
    "total_trades": 24,
    "winning_trades": 18,
    "losing_trades": 6,
    "win_rate": 75.0,
    "profit_factor": 4.2,
    "average_hold_time": "2.4 Days"
  }
}
```

---

### 5. Order Execution
* **`POST /api/v1/orders/execute`**
* **Request Body:**
```json
{
  "symbol": "RELIANCE",
  "action": "BUY",
  "quantity": 10,
  "order_type": "MARKET",
  "price": 2450.0,
  "product": "I",
  "confirmed": true
}
```
* **Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "order_id": "PAYTM_ORD_98472",
  "symbol": "RELIANCE",
  "quantity": 10,
  "price": 2450.0
}
```

---

### 6. Risk Validation Gate
* **`POST /api/v1/risk/validate`**
* **Request Body:**
```json
{
  "symbol": "TCS",
  "action": "BUY",
  "quantity": 5,
  "price": 3500.0,
  "stop_loss": 3400.0,
  "sector": "IT"
}
```
* **Response (200 OK):**
```json
{
  "decision": "APPROVED",
  "approved_quantity": 5,
  "reasons": [],
  "warnings": []
}
```
