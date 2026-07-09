import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any
import json

class TRFADatabase:
    def __init__(self, db_path="trade_forensics.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS forensic_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                signal TEXT,
                status TEXT,
                pnl REAL,
                pnl_pct REAL,
                exit_reason TEXT,
                root_cause TEXT,
                explanation TEXT,
                recommendation TEXT,
                raw_data TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_report(self, report: Dict[str, Any], raw_trade_data: Dict[str, Any]):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO forensic_reports 
            (symbol, signal, status, pnl, pnl_pct, exit_reason, root_cause, explanation, recommendation, raw_data, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report.get("symbol"),
            report.get("signal"),
            report.get("status"),
            report.get("pnl"),
            report.get("pnl_pct"),
            report.get("exit_reason"),
            report.get("root_cause"),
            report.get("explanation"),
            report.get("recommendation"),
            json.dumps(raw_trade_data),
            report.get("timestamp", datetime.now().isoformat())
        ))
        conn.commit()
        conn.close()

    def get_recent_reports(self, limit: int = 50) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM forensic_reports ORDER BY timestamp DESC LIMIT ?', (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
