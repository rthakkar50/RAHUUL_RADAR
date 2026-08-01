"""
RAHUUL RADAR — Paper Trading Platform: Database Manager (Task 10)
==================================================================
High-performance SQLite database manager for Paper Trading.
Optimized with indexes to support 10,000+ historical trades.
"""

import os
import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional
from paper_trading.paper_models import PaperOrder, PaperPosition, PaperJournalEntry, PaperValidationResult

logger = logging.getLogger("PaperDatabase")


class PaperDatabase:
    """
    High-throughput SQLite persistence for paper orders, positions, journal, and signal validation.
    """

    def __init__(self, db_path: str = "data/paper_trading.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Paper Orders Table
            c.execute('''
                CREATE TABLE IF NOT EXISTS paper_orders (
                    order_id TEXT PRIMARY KEY,
                    symbol TEXT,
                    action TEXT,
                    order_type TEXT,
                    quantity INTEGER,
                    price REAL,
                    stop_price REAL,
                    status TEXT,
                    created_at TEXT,
                    filled_at TEXT,
                    filled_price REAL,
                    strategy TEXT,
                    confidence REAL
                )
            ''')

            # Paper Positions Table
            c.execute('''
                CREATE TABLE IF NOT EXISTS paper_positions (
                    position_id TEXT PRIMARY KEY,
                    symbol TEXT,
                    action TEXT,
                    quantity INTEGER,
                    entry_price REAL,
                    current_price REAL,
                    stop_loss REAL,
                    target_1 REAL,
                    target_2 REAL,
                    target_3 REAL,
                    trailing_stop REAL,
                    current_pnl REAL,
                    pnl_pct REAL,
                    open_time TEXT,
                    holding_mins INTEGER,
                    strategy TEXT,
                    ai_confidence REAL
                )
            ''')

            # Trade Journal Table
            c.execute('''
                CREATE TABLE IF NOT EXISTS trade_journal (
                    journal_id TEXT PRIMARY KEY,
                    trade_id TEXT,
                    symbol TEXT,
                    action TEXT,
                    entry_price REAL,
                    exit_price REAL,
                    quantity INTEGER,
                    pnl REAL,
                    return_pct REAL,
                    entry_reason TEXT,
                    exit_reason TEXT,
                    ai_confidence REAL,
                    risk_reward TEXT,
                    screenshot_ref TEXT,
                    notes TEXT,
                    timestamp TEXT
                )
            ''')

            # Validation Results Table
            c.execute('''
                CREATE TABLE IF NOT EXISTS validation_results (
                    signal_id TEXT PRIMARY KEY,
                    symbol TEXT,
                    ai_signal TEXT,
                    ai_confidence REAL,
                    entry_price REAL,
                    exit_price REAL,
                    actual_outcome TEXT,
                    was_correct INTEGER,
                    accuracy_score REAL,
                    timestamp TEXT
                )
            ''')

            # High-speed indexes for 10,000+ trades
            c.execute("CREATE INDEX IF NOT EXISTS idx_journal_symbol ON trade_journal(symbol);")
            c.execute("CREATE INDEX IF NOT EXISTS idx_journal_ts ON trade_journal(timestamp);")
            c.execute("CREATE INDEX IF NOT EXISTS idx_val_symbol ON validation_results(symbol);")
            c.execute("CREATE INDEX IF NOT EXISTS idx_orders_symbol ON paper_orders(symbol);")

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize Paper Trading DB: {e}")

    def save_order(self, order: PaperOrder):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO paper_orders (
                    order_id, symbol, action, order_type, quantity, price, stop_price,
                    status, created_at, filled_at, filled_price, strategy, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order.order_id, order.symbol, order.action, order.order_type, order.quantity,
                order.price, order.stop_price, order.status, order.created_at, order.filled_at or "",
                order.filled_price, order.strategy, order.confidence
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error saving paper order {order.order_id}: {e}")

    def save_journal_entry(self, entry: PaperJournalEntry):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO trade_journal (
                    journal_id, trade_id, symbol, action, entry_price, exit_price, quantity,
                    pnl, return_pct, entry_reason, exit_reason, ai_confidence, risk_reward,
                    screenshot_ref, notes, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.journal_id, entry.trade_id, entry.symbol, entry.action, entry.entry_price,
                entry.exit_price, entry.quantity, entry.pnl, entry.return_pct, entry.entry_reason,
                entry.exit_reason, entry.ai_confidence, entry.risk_reward, entry.screenshot_ref,
                entry.notes, entry.timestamp
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error saving journal entry {entry.journal_id}: {e}")

    def save_validation_result(self, res: PaperValidationResult):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO validation_results (
                    signal_id, symbol, ai_signal, ai_confidence, entry_price, exit_price,
                    actual_outcome, was_correct, accuracy_score, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                res.signal_id, res.symbol, res.ai_signal, res.ai_confidence, res.entry_price,
                res.exit_price, res.actual_outcome, 1 if res.was_correct else 0,
                res.accuracy_score, res.timestamp
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error saving validation result {res.signal_id}: {e}")

    def get_journal_entries(self, limit: int = 100) -> List[PaperJournalEntry]:
        entries = []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM trade_journal ORDER BY timestamp DESC LIMIT ?", (limit,))
            for r in c.fetchall():
                entries.append(PaperJournalEntry(
                    journal_id=r["journal_id"],
                    trade_id=r["trade_id"],
                    symbol=r["symbol"],
                    action=r["action"],
                    entry_price=r["entry_price"],
                    exit_price=r["exit_price"],
                    quantity=r["quantity"],
                    pnl=r["pnl"],
                    return_pct=r["return_pct"],
                    entry_reason=r["entry_reason"],
                    exit_reason=r["exit_reason"],
                    ai_confidence=r["ai_confidence"],
                    risk_reward=r["risk_reward"],
                    screenshot_ref=r["screenshot_ref"],
                    notes=r["notes"],
                    timestamp=r["timestamp"]
                ))
            conn.close()
        except Exception as e:
            logger.error(f"Error fetching journal entries: {e}")
        return entries
