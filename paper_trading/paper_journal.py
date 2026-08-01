"""
RAHUUL RADAR — Paper Trading Platform: Trade Journal (Task 4)
=============================================================
Automated Trade Journaling Engine.
Logs Entry, Exit, Reasons, AI Confidence, Risk/Reward, Screenshot refs, and Notes.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from paper_trading.paper_models import PaperJournalEntry
from paper_trading.paper_database import PaperDatabase


class PaperJournal:
    """
    Automated Trade Journaling Center.
    """

    def __init__(self, db: Optional[PaperDatabase] = None):
        self.db = db or PaperDatabase()

    def record_completed_trade(
        self,
        trade_id: str,
        symbol: str,
        action: str,
        entry_price: float,
        exit_price: float,
        quantity: int,
        pnl: float,
        return_pct: float,
        entry_reason: str,
        exit_reason: str,
        ai_confidence: float,
        risk_reward: str,
        screenshot_ref: str = "",
        notes: str = ""
    ) -> PaperJournalEntry:
        """Records a completed trade into the SQLite journal database."""
        journal_id = f"JRN-{uuid.uuid4().hex[:8].upper()}"
        now_str = datetime.now().isoformat()

        entry = PaperJournalEntry(
            journal_id=journal_id,
            trade_id=trade_id,
            symbol=symbol.upper(),
            action=action.upper(),
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=quantity,
            pnl=pnl,
            return_pct=return_pct,
            entry_reason=entry_reason,
            exit_reason=exit_reason,
            ai_confidence=ai_confidence,
            risk_reward=risk_reward,
            screenshot_ref=screenshot_ref or f"screenshots/{symbol}_{trade_id}.png",
            notes=notes or "Automated paper trade execution",
            timestamp=now_str
        )

        self.db.save_journal_entry(entry)
        return entry

    def get_recent_journal_entries(self, limit: int = 50) -> List[PaperJournalEntry]:
        return self.db.get_journal_entries(limit=limit)
