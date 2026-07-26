# RAHUUL RADAR — Database Specification (v1.1)

All databases are SQLite3 instances stored in `data/`. Connections use Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) and a busy timeout of 5,000ms.

---

## Active SQLite Databases

```
data/
 ├── radar.db           (Watchlist, Legacy Trades & AI Decisions)
 ├── trade_journal.db   (Production Trade Journal & Analytics)
 ├── paper_trading.db   (Paper Trading Portfolio & Active Positions)
 ├── order_audit_log.db (Live Order Execution Audit Log)
 └── risk_state.db      (Sprint M6 Daily Risk Tracker & Locks)
```

---

## Database Schemas

### 1. `data/radar.db`
#### Table: `watchlist`
```sql
CREATE TABLE watchlist (
    symbol TEXT PRIMARY KEY,
    added_at TEXT
);
```

#### Table: `master_ai_decisions`
```sql
CREATE TABLE master_ai_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    symbol TEXT,
    signal TEXT,
    reasons TEXT,
    score REAL,
    status TEXT,
    result TEXT DEFAULT 'PENDING'
);
```

---

### 2. `data/trade_journal.db`
#### Table: `trades`
```sql
CREATE TABLE trades (
    id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    signal TEXT NOT NULL,
    entry_price REAL NOT NULL,
    exit_price REAL NOT NULL,
    sl REAL,
    target REAL,
    qty INTEGER NOT NULL,
    pnl REAL NOT NULL,
    pnl_pct REAL NOT NULL,
    r_multiple TEXT,
    trade_date TEXT NOT NULL,
    duration TEXT,
    result TEXT NOT NULL,
    exit_reason TEXT,
    ai_score REAL,
    confidence REAL,
    trend TEXT,
    momentum TEXT,
    volume TEXT,
    structure TEXT
);
```

---

### 3. `data/paper_trading.db`
#### Table: `portfolio`
```sql
CREATE TABLE portfolio (
    id INTEGER PRIMARY KEY,
    capital REAL,
    realized_pnl REAL,
    unrealized_pnl REAL,
    updated_at TEXT
);
```

#### Table: `positions`
```sql
CREATE TABLE positions (
    id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    order_type TEXT,
    direction TEXT NOT NULL,
    entry_price REAL NOT NULL,
    sl REAL NOT NULL,
    target REAL NOT NULL,
    qty INTEGER NOT NULL,
    current_price REAL NOT NULL,
    unrealized_pnl REAL NOT NULL,
    pnl_pct REAL NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

---

### 4. `data/order_audit_log.db`
#### Table: `audit_logs`
```sql
CREATE TABLE audit_logs (
    audit_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    symbol TEXT NOT NULL,
    action TEXT NOT NULL,
    order_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    trigger_price REAL,
    request_payload TEXT,
    response_payload TEXT,
    http_status INTEGER,
    latency_ms REAL,
    status TEXT NOT NULL,
    error_message TEXT
);
```

---

### 5. `data/risk_state.db`
#### Table: `daily_state`
```sql
CREATE TABLE daily_state (
    trade_date TEXT PRIMARY KEY,
    realized_pnl REAL NOT NULL,
    orders_count INTEGER NOT NULL,
    consecutive_losses INTEGER NOT NULL,
    kill_switch INTEGER NOT NULL,
    auto_trading INTEGER NOT NULL
);
```

#### Table: `open_positions`
```sql
CREATE TABLE open_positions (
    symbol TEXT PRIMARY KEY,
    trade_date TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    entry_price REAL NOT NULL,
    stop_loss REAL NOT NULL,
    sector TEXT NOT NULL,
    product TEXT NOT NULL
);
```

#### Table: `order_events`
```sql
CREATE TABLE order_events (
    event_id TEXT PRIMARY KEY,
    trade_date TEXT NOT NULL,
    symbol TEXT NOT NULL,
    action TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    status TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
```
