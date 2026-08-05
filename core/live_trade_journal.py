# RAHUUL_RADAR Enterprise Live Trade Journal Engine
# Production-grade persistent trade journal manager for real runtime events

import os
import json
import sqlite3
import csv
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "live_journal.db")
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "live_journal_export.csv")
JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "live_journal.json")

class LiveTradeJournalEngine:
    """Manages persistent live trade journal records across SQLite, CSV, and JSON."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initializes SQLite schema for permanent trade records."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS live_journal (
                trade_id TEXT PRIMARY KEY,
                date TEXT,
                time TEXT,
                scanner TEXT,
                symbol TEXT,
                signal TEXT,
                entry REAL,
                stop_loss REAL,
                target1 REAL,
                target2 REAL,
                confidence REAL,
                composite_score REAL,
                market_status TEXT,
                provider TEXT,
                highest_price REAL,
                lowest_price REAL,
                current_price REAL,
                current_pnl REAL,
                target_hit INTEGER,
                sl_hit INTEGER,
                holding_time TEXT,
                trade_status TEXT,
                created_at REAL,
                updated_at REAL
            )
        """)
        conn.commit()
        conn.close()

    def record_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically creates ONE journal record when any scanner generates a signal."""
        symbol = signal_data.get("Symbol", "UNKNOWN").strip().upper()
        scanner = signal_data.get("source_engine", signal_data.get("Scanner", "Swing")).capitalize()
        now = datetime.now()

        trade_id = f"TRD-{now.strftime('%Y%m%d')}-{symbol.replace('.NS', '')}-{int(time.time() * 1000) % 10000}"
        
        entry = float(signal_data.get("Entry", signal_data.get("Price", 0.0)))
        sl = float(signal_data.get("Stop Loss", entry * 0.97))
        t1 = float(signal_data.get("Target 1", entry * 1.05))
        t2 = float(signal_data.get("Target 2", entry * 1.10))
        confidence = float(signal_data.get("Confidence", 80.0))
        score = float(signal_data.get("Score", 80.0))
        market_status = signal_data.get("market_status", "CLOSED")
        provider = signal_data.get("provider", "Paytm Money (Live)")

        record = {
            "trade_id": trade_id,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "scanner": scanner,
            "symbol": symbol,
            "signal": signal_data.get("Signal", "BUY"),
            "entry": entry,
            "stop_loss": sl,
            "target1": t1,
            "target2": t2,
            "confidence": confidence,
            "composite_score": score,
            "market_status": market_status,
            "provider": provider,
            "highest_price": entry,
            "lowest_price": entry,
            "current_price": entry,
            "current_pnl": 0.0,
            "target_hit": 0,
            "sl_hit": 0,
            "holding_time": "0m",
            "trade_status": "OPEN",
            "created_at": time.time(),
            "updated_at": time.time(),
        }

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT OR IGNORE INTO live_journal (
                trade_id, date, time, scanner, symbol, signal, entry, stop_loss, target1, target2,
                confidence, composite_score, market_status, provider, highest_price, lowest_price,
                current_price, current_pnl, target_hit, sl_hit, holding_time, trade_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(record.values()))
        conn.commit()
        conn.close()

        self._export_json_and_csv()
        return record

    def update_price(self, trade_id: str, current_price: float) -> Optional[Dict[str, Any]]:
        """Updates trade metrics as market price changes."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM live_journal WHERE trade_id = ?", (trade_id,))
        row = c.fetchone()
        if not row or row["trade_status"] == "CLOSED":
            conn.close()
            return None

        trade = dict(row)
        entry = float(trade["entry"])
        sl = float(trade["stop_loss"])
        t1 = float(trade["target1"])
        sig = trade["signal"]

        highest = max(float(trade["highest_price"]), current_price)
        lowest = min(float(trade["lowest_price"]), current_price)
        
        pnl = ((current_price - entry) / entry * 100) if sig == "BUY" else ((entry - current_price) / entry * 100)
        
        target_hit = 1 if (current_price >= t1 if sig == "BUY" else current_price <= t1) else trade["target_hit"]
        sl_hit = 1 if (current_price <= sl if sig == "BUY" else current_price >= sl) else trade["sl_hit"]

        status = trade["trade_status"]
        if target_hit:
            status = "TARGET HIT"
        elif sl_hit:
            status = "STOP HIT"

        created_at = float(trade["created_at"])
        elapsed_mins = int((time.time() - created_at) / 60)
        holding_time = f"{elapsed_mins}m" if elapsed_mins < 1440 else f"{elapsed_mins // 1440}d"

        c.execute("""
            UPDATE live_journal SET
                highest_price = ?, lowest_price = ?, current_price = ?, current_pnl = ?,
                target_hit = ?, sl_hit = ?, holding_time = ?, trade_status = ?, updated_at = ?
            WHERE trade_id = ?
        """, (highest, lowest, current_price, pnl, target_hit, sl_hit, holding_time, status, time.time(), trade_id))
        conn.commit()
        conn.close()

        self._export_json_and_csv()
        return self.get_trade_by_id(trade_id)

    def close_trade(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """Freezes record forever when trade closes."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE live_journal SET trade_status = 'CLOSED', updated_at = ? WHERE trade_id = ?", (time.time(), trade_id))
        conn.commit()
        conn.close()
        self._export_json_and_csv()
        return self.get_trade_by_id(trade_id)

    def get_all_trades(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM live_journal ORDER BY created_at DESC")
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_trade_by_id(self, trade_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM live_journal WHERE trade_id = ?", (trade_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_open_trades(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM live_journal WHERE trade_status != 'CLOSED' ORDER BY created_at DESC")
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_closed_trades(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM live_journal WHERE trade_status = 'CLOSED' ORDER BY created_at DESC")
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _export_json_and_csv(self):
        trades = self.get_all_trades()
        with open(JSON_PATH, "w") as f:
            json.dump(trades, f, indent=2)

        if trades:
            keys = trades[0].keys()
            with open(CSV_PATH, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(trades)

# Global singleton instance
journal_engine = LiveTradeJournalEngine()
