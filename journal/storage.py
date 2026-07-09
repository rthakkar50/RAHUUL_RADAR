import sqlite3
import json
from typing import List, Optional
from datetime import datetime
from .models import TradeEntry

class JournalStorage:
    def __init__(self, db_path: str = "database/journal.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    trade_id TEXT PRIMARY KEY,
                    symbol TEXT,
                    entry_price REAL,
                    exit_price REAL,
                    stop_loss REAL,
                    target REAL,
                    risk_amount REAL,
                    realized_rr REAL,
                    pnl REAL,
                    screenshot_path TEXT,
                    emotion_notes TEXT,
                    ai_notes TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()
            
    def save_trade(self, trade: TradeEntry):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trades (trade_id, symbol, entry_price, exit_price, stop_loss, target, risk_amount, realized_rr, pnl, screenshot_path, emotion_notes, ai_notes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.trade_id, trade.symbol, trade.entry_price, trade.exit_price, trade.stop_loss, trade.target,
                trade.risk_amount, trade.realized_rr, trade.pnl, trade.screenshot_path, trade.emotion_notes, trade.ai_notes,
                trade.timestamp.isoformat()
            ))
            conn.commit()
            
    def get_all_trades(self) -> List[TradeEntry]:
        trades = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM trades ORDER BY timestamp ASC')
            for row in cursor.fetchall():
                trades.append(TradeEntry(
                    trade_id=row[0], symbol=row[1], entry_price=row[2], exit_price=row[3],
                    stop_loss=row[4], target=row[5], risk_amount=row[6], realized_rr=row[7],
                    pnl=row[8], screenshot_path=row[9], emotion_notes=row[10], ai_notes=row[11],
                    timestamp=datetime.fromisoformat(row[12])
                ))
        return trades
