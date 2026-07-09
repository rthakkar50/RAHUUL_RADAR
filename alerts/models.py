from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class AlertType(Enum):
    BREAKOUT = "BREAKOUT"
    BREAKDOWN = "BREAKDOWN"
    HIGH_VOLUME = "HIGH_VOLUME"
    TARGET_HIT = "TARGET_HIT"
    SL_HIT = "SL_HIT"

@dataclass
class AlertEvent:
    alert_type: AlertType
    symbol: str
    price: float
    message: str
    timestamp: datetime = datetime.now()
