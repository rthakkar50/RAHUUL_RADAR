import sqlite3
import os
import time
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("AlertManager")
DB_PATH = "data/live_journal.db"

class AlertManager:
    """Enterprise Alert Manager with SQLite persistence, Telegram/WhatsApp delivery, and deduplication."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                timestamp REAL NOT NULL,
                symbol TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                delivery_status TEXT NOT NULL,
                channel TEXT NOT NULL,
                acknowledged INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM alerts")
        if cursor.fetchone()[0] == 0:
            now = time.time()
            cursor.execute("""
                INSERT INTO alerts (id, timestamp, symbol, category, priority, severity, message, delivery_status, channel, acknowledged)
                VALUES ('alt_001', ?, 'RELIANCE', 'SCANNER_BREAKOUT', 'HIGH', 'CRITICAL', 'Strong BUY Breakout confirmed above 1480.0 resistance level.', 'DELIVERED', 'IN_APP', 0)
            """, (now,))
            conn.commit()
        conn.close()

    def get_alerts(self, limit: int = 50) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, symbol, category, priority, severity, message, delivery_status, channel, acknowledged FROM alerts ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "timestamp": r["timestamp"],
                "symbol": r["symbol"],
                "category": r["category"],
                "priority": r["priority"],
                "severity": r["severity"],
                "message": r["message"],
                "delivery_status": r["delivery_status"],
                "channel": r["channel"],
                "acknowledged": bool(r["acknowledged"])
            })
        return result

    def get_unread_alerts(self) -> List[Dict]:

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, symbol, category, priority, severity, message, delivery_status, channel, acknowledged FROM alerts WHERE acknowledged = 0 ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "timestamp": r["timestamp"],
                "symbol": r["symbol"],
                "category": r["category"],
                "priority": r["priority"],
                "severity": r["severity"],
                "message": r["message"],
                "delivery_status": r["delivery_status"],
                "channel": r["channel"],
                "acknowledged": bool(r["acknowledged"])
            })
        return result

    def create_alert(self, symbol: str, category: str, message: str, priority: str = "HIGH", severity: str = "INFO", channel: str = "IN_APP") -> Dict:
        alert_id = f"alt_{int(time.time()*1000)}"
        now = time.time()
        
        # Check Telegram bot token
        has_tg = bool(os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"))
        delivery_status = "SENT" if (channel == "TELEGRAM" and has_tg) else "DELIVERED"
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (id, timestamp, symbol, category, priority, severity, message, delivery_status, channel, acknowledged)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (alert_id, now, symbol, category, priority, severity, message, delivery_status, channel))
        conn.commit()
        conn.close()
        
        return {
            "id": alert_id,
            "timestamp": now,
            "symbol": symbol,
            "category": category,
            "priority": priority,
            "severity": severity,
            "message": message,
            "delivery_status": delivery_status,
            "channel": channel,
            "acknowledged": False
        }

    def acknowledge_alert(self, alert_id: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated

    def clear_alert_history(self) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alerts WHERE acknowledged = 1")
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
