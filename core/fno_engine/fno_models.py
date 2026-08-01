"""
RAHUUL RADAR — F&O Trading Engine: Domain Models & Dataclasses
=============================================================
Defines standard data contracts for Options & Futures trading.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import date, datetime


class InstrumentType(Enum):
    INDEX_OPTION = "INDEX_OPTION"
    INDEX_FUTURE = "INDEX_FUTURE"
    STOCK_OPTION = "STOCK_OPTION"
    STOCK_FUTURE = "STOCK_FUTURE"


class OptionType(Enum):
    CALL = "CE"
    PUT = "PE"


class OIBuildUp(Enum):
    LONG_BUILDUP = "LONG_BUILDUP"
    SHORT_BUILDUP = "SHORT_BUILDUP"
    SHORT_COVERING = "SHORT_COVERING"
    LONG_UNWINDING = "LONG_UNWINDING"
    NEUTRAL = "NEUTRAL"


@dataclass
class FNOContract:
    symbol: str
    underlying: str
    strike: float
    option_type: str  # 'CE' or 'PE' or 'FUT'
    expiry: str
    lot_size: int
    exchange: str = "NSE"
    instrument_type: str = "INDEX_OPTION"


@dataclass
class OptionChainItem:
    strike_price: float
    call_oi: int
    put_oi: int
    call_change_oi: int
    put_change_oi: int
    call_ltp: float
    put_ltp: float
    call_volume: int
    put_volume: int
    call_iv: float
    put_iv: float
    call_bid: float = 0.0
    call_ask: float = 0.0
    put_bid: float = 0.0
    put_ask: float = 0.0
    open_price: float = 0.0
    high_price: float = 0.0
    low_price: float = 0.0
    close_price: float = 0.0


@dataclass
class Greeks:
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


@dataclass
class IVMetrics:
    current_iv: float
    iv_rank: float
    iv_percentile: float
    iv_expansion: bool
    iv_crush: bool


@dataclass
class PCRMetrics:
    total_pcr: float
    strike_pcr: float
    weighted_pcr: float
    historical_pcr: float


@dataclass
class MaxPainMetrics:
    max_pain_strike: float
    total_pain: float
    support_level: float
    resistance_level: float


@dataclass
class FNORiskReport:
    lot_size: int
    num_lots: int
    capital_allocation: float
    margin_required: float
    max_risk: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    risk_reward: float
    max_daily_loss: float


@dataclass
class FNOSignal:
    symbol: str
    underlying: str
    expiry: str
    strike: float
    option_type: str
    action: str
    confidence: float
    entry: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    risk_reward: str
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Symbol": self.symbol,
            "Underlying": self.underlying,
            "Expiry": self.expiry,
            "Strike": self.strike,
            "OptionType": self.option_type,
            "Action": self.action,
            "Confidence": self.confidence,
            "Entry": self.entry,
            "StopLoss": self.stop_loss,
            "Target1": self.target_1,
            "Target2": self.target_2,
            "Target3": self.target_3,
            "RiskReward": self.risk_reward,
            "Reasons": self.reasons
        }
