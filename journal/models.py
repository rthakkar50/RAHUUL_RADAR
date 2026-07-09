from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class TradeEntry:
    trade_id: str
    symbol: str
    entry_price: float
    exit_price: float
    stop_loss: float
    target: float
    risk_amount: float
    realized_rr: float
    pnl: float
    screenshot_path: Optional[str]
    emotion_notes: str
    ai_notes: str
    timestamp: datetime
    
    @property
    def is_win(self) -> bool:
        return self.pnl > 0

@dataclass
class JournalStats:
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    average_rr: float
    max_drawdown: float
    profit_factor: float
    net_pnl: float
