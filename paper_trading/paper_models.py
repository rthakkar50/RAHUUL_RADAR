"""
RAHUUL RADAR — Paper Trading Platform: Domain Models
=====================================================
Data contracts and domain models for paper trading simulation.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


class PaperOrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class PaperOrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class PaperOrder:
    order_id: str
    symbol: str
    action: str  # BUY / SELL
    order_type: str  # MARKET / LIMIT / STOP / STOP_LIMIT
    quantity: int
    price: float
    stop_price: float = 0.0
    status: str = "PENDING"
    created_at: str = ""
    filled_at: Optional[str] = None
    filled_price: float = 0.0
    strategy: str = "SWING"
    confidence: float = 0.0


@dataclass
class PaperPosition:
    position_id: str
    symbol: str
    action: str
    quantity: int
    entry_price: float
    current_price: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    trailing_stop: float = 0.0
    current_pnl: float = 0.0
    pnl_pct: float = 0.0
    open_time: str = ""
    holding_mins: int = 0
    strategy: str = "SWING"
    ai_confidence: float = 0.0


@dataclass
class PaperAccountSummary:
    initial_balance: float
    cash_balance: float
    margin_used: float
    buying_power: float
    equity: float
    todays_pnl: float
    total_pnl: float
    max_drawdown_pct: float


@dataclass
class PaperJournalEntry:
    journal_id: str
    trade_id: str
    symbol: str
    action: str
    entry_price: float
    exit_price: float
    quantity: int
    pnl: float
    return_pct: float
    entry_reason: str
    exit_reason: str
    ai_confidence: float
    risk_reward: str
    screenshot_ref: str = ""
    notes: str = ""
    timestamp: str = ""


@dataclass
class PaperPerformanceMetrics:
    total_trades: int
    win_rate: float
    loss_rate: float
    profit_factor: float
    sharpe_ratio: float
    expectancy: float
    avg_winner: float
    avg_loser: float
    max_drawdown_pct: float
    avg_holding_time_mins: float


@dataclass
class PaperValidationResult:
    signal_id: str
    symbol: str
    ai_signal: str
    ai_confidence: float
    entry_price: float
    exit_price: float
    actual_outcome: str  # WIN / LOSS / BREAKEVEN
    was_correct: bool
    accuracy_score: float
    timestamp: str = ""
