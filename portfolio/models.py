from dataclasses import dataclass
from typing import Dict

@dataclass
class PortfolioStats:
    total_capital: float
    invested_capital: float
    available_cash: float
    total_mtm: float
    overall_risk_pct: float

@dataclass
class SectorAllocation:
    allocation_pct: Dict[str, float]
