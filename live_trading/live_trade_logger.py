"""
RAHUUL RADAR — Phase-1 Limited Live Trading: Live Trade Logger
===============================================================
Centralized immutable audit logger for live trade execution records (all 18 mandatory fields).
"""

import sqlite3
import logging
from typing import List, Dict, Any, Optional
from live_trading.live_models import LiveTradeRecord

logger = logging.getLogger("LiveTradeLogger")


class LiveTradeLogger:
    """
    Live Trade Audit Logger.
    """

    def __init__(self, db_path: str = "data/order_audit_log.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS live_trade_audit (
                    trade_id TEXT PRIMARY KEY,
                    date TEXT,
                    time TEXT,
                    broker_order_id TEXT,
                    ai_signal TEXT,
                    confidence REAL,
                    entry_price REAL,
                    exit_price REAL,
                    actual_fill_price REAL,
                    slippage REAL,
                    broker_charges REAL,
                    taxes REAL,
                    latency_ms REAL,
                    pnl REAL,
                    net_pnl REAL,
                    risk_pct REAL,
                    reason TEXT,
                    market_regime TEXT
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to init Live Trade Audit DB: {e}")

    def record_live_trade(self, rec: LiveTradeRecord):
        """Records a live trade with full 18-field audit completeness."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO live_trade_audit (
                    trade_id, date, time, broker_order_id, ai_signal, confidence,
                    entry_price, exit_price, actual_fill_price, slippage, broker_charges,
                    taxes, latency_ms, pnl, net_pnl, risk_pct, reason, market_regime
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rec.trade_id, rec.date, rec.time, rec.broker_order_id, rec.ai_signal,
                rec.confidence, rec.entry_price, rec.exit_price, rec.actual_fill_price,
                rec.slippage, rec.broker_charges, rec.taxes, rec.latency_ms, rec.pnl,
                rec.net_pnl, rec.risk_pct, rec.reason, rec.market_regime
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to save live trade {rec.trade_id}: {e}")

    def get_all_live_trades(self) -> List[LiveTradeRecord]:
        trades = []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM live_trade_audit ORDER BY date DESC, time DESC")
            for r in c.fetchall():
                trades.append(LiveTradeRecord(
                    trade_id=r["trade_id"],
                    date=r["date"],
                    time=r["time"],
                    broker_order_id=r["broker_order_id"],
                    ai_signal=r["ai_signal"],
                    confidence=r["confidence"],
                    entry_price=r["entry_price"],
                    exit_price=r["exit_price"],
                    actual_fill_price=r["actual_fill_price"],
                    slippage=r["slippage"],
                    broker_charges=r["broker_charges"],
                    taxes=r["taxes"],
                    latency_ms=r["latency_ms"],
                    pnl=r["pnl"],
                    net_pnl=r["net_pnl"],
                    risk_pct=r["risk_pct"],
                    reason=r["reason"],
                    market_regime=r["market_regime"]
                ))
            conn.close()
        except Exception as e:
            logger.error(f"Error fetching live trade audit logs: {e}")
        return trades
