from dataclasses import dataclass
from typing import Optional

@dataclass
class RiskProfile:
    account_size: float
    risk_per_trade_pct: float
    max_daily_loss_pct: float
    max_weekly_loss_pct: float
    max_monthly_loss_pct: float
    max_open_trades: int
    max_sector_exposure_pct: float
    prop_firm: str = "custom"

@dataclass
class RiskResult:
    approved: bool
    reason: str
    risk_pct: float
    lot_size: int
    capital_required: float
    maximum_loss: float
    recommended_target: float
    recommended_rr: float
