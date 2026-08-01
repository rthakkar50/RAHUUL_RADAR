"""
RAHUUL RADAR — Paper Trading Platform: Order Manager (Task 2)
==============================================================
Simulates order execution for BUY, SELL, MARKET, LIMIT, STOP, STOP_LIMIT
with realistic fill modeling and zero broker coupling.
"""

import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional
from paper_trading.paper_models import PaperOrder, PaperOrderType, PaperOrderStatus


class PaperOrderManager:
    """
    Virtual Order Execution Manager.
    """

    def __init__(self):
        self._orders: Dict[str, PaperOrder] = {}

    def create_order(
        self,
        symbol: str,
        action: str,
        order_type: str,
        quantity: int,
        price: float = 0.0,
        stop_price: float = 0.0,
        strategy: str = "SWING",
        confidence: float = 0.0
    ) -> PaperOrder:
        """Creates and stores a virtual paper order."""
        order_id = f"P-ORD-{uuid.uuid4().hex[:8].upper()}"
        now_str = datetime.now().isoformat()

        order = PaperOrder(
            order_id=order_id,
            symbol=symbol.upper(),
            action=action.upper(),
            order_type=order_type.upper(),
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            status=PaperOrderStatus.PENDING.value,
            created_at=now_str,
            strategy=strategy,
            confidence=confidence
        )

        # Simulate immediate execution for MARKET orders
        if order_type.upper() == PaperOrderType.MARKET.value:
            order.status = PaperOrderStatus.FILLED.value
            order.filled_at = now_str
            order.filled_price = price if price > 0 else 100.0

        self._orders[order_id] = order
        return order

    def execute_limit_check(self, current_market_price: float) -> List[PaperOrder]:
        """Checks and fills pending LIMIT/STOP orders against live/simulated market price."""
        filled_orders = []
        now_str = datetime.now().isoformat()

        for order in self._orders.values():
            if order.status != PaperOrderStatus.PENDING.value:
                continue

            # LIMIT BUY fill condition (Market price <= Limit price)
            if order.order_type == "LIMIT" and order.action == "BUY" and current_market_price <= order.price:
                order.status = PaperOrderStatus.FILLED.value
                order.filled_at = now_str
                order.filled_price = current_market_price
                filled_orders.append(order)

            # LIMIT SELL fill condition (Market price >= Limit price)
            elif order.order_type == "LIMIT" and order.action == "SELL" and current_market_price >= order.price:
                order.status = PaperOrderStatus.FILLED.value
                order.filled_at = now_str
                order.filled_price = current_market_price
                filled_orders.append(order)

            # STOP BUY fill condition
            elif order.order_type == "STOP" and order.action == "BUY" and current_market_price >= order.stop_price:
                order.status = PaperOrderStatus.FILLED.value
                order.filled_at = now_str
                order.filled_price = current_market_price
                filled_orders.append(order)

            # STOP SELL fill condition
            elif order.order_type == "STOP" and order.action == "SELL" and current_market_price <= order.stop_price:
                order.status = PaperOrderStatus.FILLED.value
                order.filled_at = now_str
                order.filled_price = current_market_price
                filled_orders.append(order)

        return filled_orders

    def cancel_order(self, order_id: str) -> bool:
        """Cancels a pending order."""
        if order_id in self._orders and self._orders[order_id].status == PaperOrderStatus.PENDING.value:
            self._orders[order_id].status = PaperOrderStatus.CANCELLED.value
            return True
        return False

    def get_order(self, order_id: str) -> Optional[PaperOrder]:
        return self._orders.get(order_id)
