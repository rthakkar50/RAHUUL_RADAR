from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class PaperPosition:
    position_id: str
    symbol: str
    direction: str # BUY / SELL
    qty: int
    entry_price: float
    current_price: float
    sl: float
    target: float
    target_1: float = 0.0
    target_2: float = 0.0
    target_3: float = 0.0
    trailing_stop: float = 0.0
    time_exit_dt: Optional[str] = None
    unrealized_pnl: float = 0.0
    used_margin: float = 0.0
    status: str = 'OPEN'
    entry_time: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    exit_price: float = 0.0
    exit_time: str = ""
    realized_pnl: float = 0.0
    charges: float = 0.0

@dataclass
class PaperPortfolioState:
    virtual_capital: float
    available_cash: float
    used_margin: float
    realized_pnl: float
    unrealized_pnl: float
    total_equity: float
    open_positions: Dict[str, PaperPosition] = field(default_factory=dict)
    closed_positions: List[PaperPosition] = field(default_factory=list)
