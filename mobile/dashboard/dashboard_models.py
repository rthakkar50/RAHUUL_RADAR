"""
RAHUUL RADAR — Mobile Dashboard: Domain Models (Task 1 - 7)
============================================================
Data transfer objects and models for the Enterprise Mobile Dashboard.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class MarketStatusSummary:
    market_state: str  # "OPEN" / "CLOSED"
    nifty_price: float
    nifty_change: float
    banknifty_price: float
    banknifty_change: float
    regime: str


@dataclass
class AccountStatusSummary:
    broker_name: str
    is_connected: bool
    total_capital: float
    available_margin: float
    used_margin: float


@dataclass
class PortfolioSummary:
    total_portfolio_value: float
    todays_pnl: float
    todays_pnl_pct: float
    total_pnl: float
    total_pnl_pct: float
    winning_rate: float
    drawdown: float
    open_positions_count: int
    holdings_count: int


@dataclass
class WatchlistCardItem:
    symbol: str
    underlying: str
    signal: str
    confidence: float
    entry: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    risk_reward: str
    ai_reason: str
    mode: str = "SWING"  # SWING / FNO / INTRADAY
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "underlying": self.underlying,
            "signal": self.signal,
            "confidence": self.confidence,
            "entry": self.entry,
            "stop_loss": self.stop_loss,
            "target_1": self.target_1,
            "target_2": self.target_2,
            "target_3": self.target_3,
            "risk_reward": self.risk_reward,
            "ai_reason": self.ai_reason,
            "mode": self.mode,
            "timestamp": self.timestamp
        }


@dataclass
class RiskDashboardSummary:
    current_risk_pct: float
    daily_loss: float
    max_daily_loss: float
    margin_used_pct: float
    sector_exposure: Dict[str, float]
    lot_exposure: Dict[str, int]
    risk_level: str  # "LOW", "MODERATE", "HIGH", "CRITICAL"


@dataclass
class AnalyticsSummary:
    win_rate: float
    profit_curve: List[float]
    monthly_returns: Dict[str, float]
    strategy_performance: Dict[str, float]
    best_trade: Dict[str, Any]
    worst_trade: Dict[str, Any]
    avg_holding_time_mins: float


@dataclass
class NotificationItem:
    id: str
    type: str  # "AI_SIGNAL", "RISK_ALERT", "MARGIN_ALERT", "SYSTEM_ALERT", "EXECUTION_ALERT"
    title: str
    message: str
    timestamp: str
    is_read: bool = False
