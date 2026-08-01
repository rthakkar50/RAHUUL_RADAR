"""
RAHUUL RADAR — Paper Trading Platform: Virtual Account (Task 1)
===============================================================
Manages virtual cash balance, margin, buying power, equity, drawdown, and daily P&L.
"""

from typing import Dict, Any
from paper_trading.paper_models import PaperAccountSummary


class PaperAccount:
    """
    Virtual Paper Trading Account Manager.
    """

    def __init__(self, initial_capital: float = 1000000.0):
        self.initial_capital = initial_capital
        self.cash_balance = initial_capital
        self.margin_used = 0.0
        self.todays_pnl = 0.0
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.peak_equity = initial_capital

    @property
    def equity(self) -> float:
        return round(self.cash_balance + self.unrealized_pnl, 2)

    @property
    def total_pnl(self) -> float:
        return round(self.realized_pnl + self.unrealized_pnl, 2)

    @property
    def buying_power(self) -> float:
        return round(max(self.cash_balance - self.margin_used, 0.0) * 5.0, 2)  # 5x intraday/swing leverage

    @property
    def drawdown_pct(self) -> float:
        if self.equity >= self.peak_equity:
            self.peak_equity = self.equity
            return 0.0
        dd = ((self.peak_equity - self.equity) / max(self.peak_equity, 1.0)) * 100.0
        return round(dd, 2)

    def allocate_margin(self, amount: float) -> bool:
        """Allocates margin for a new paper position."""
        if amount > (self.cash_balance - self.margin_used):
            return False
        self.margin_used += amount
        return True

    def release_margin(self, amount: float):
        """Releases margin upon position closure."""
        self.margin_used = max(self.margin_used - amount, 0.0)

    def update_pnl(self, realized: float = 0.0, unrealized: float = 0.0):
        """Updates account P&L metrics."""
        self.realized_pnl += realized
        self.todays_pnl += realized
        self.cash_balance += realized
        self.unrealized_pnl = unrealized

    def get_summary(self) -> PaperAccountSummary:
        return PaperAccountSummary(
            initial_balance=self.initial_capital,
            cash_balance=round(self.cash_balance, 2),
            margin_used=round(self.margin_used, 2),
            buying_power=self.buying_power,
            equity=self.equity,
            todays_pnl=round(self.todays_pnl, 2),
            total_pnl=self.total_pnl,
            max_drawdown_pct=self.drawdown_pct
        )
