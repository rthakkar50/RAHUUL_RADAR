from dataclasses import dataclass
from typing import Optional
from enum import Enum
from datetime import datetime

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "SL"
    STOP_LOSS_MARKET = "SL-M"

class OrderStatus(Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    COMPLETE = "COMPLETE"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

@dataclass
class Order:
    order_id: str
    symbol: str
    qty: int
    order_type: OrderType
    price: float
    trigger_price: float
    status: OrderStatus
    timestamp: datetime

@dataclass
class Position:
    symbol: str
    qty: int
    avg_price: float
    ltp: float
    realized_pnl: float
    unrealized_pnl: float
    
    @property
    def total_pnl(self) -> float:
        return self.realized_pnl + self.unrealized_pnl

@dataclass
class Funds:
    available_margin: float
    used_margin: float
    available_cash: float
    collateral: float
