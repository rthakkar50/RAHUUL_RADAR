"""
RAHUUL RADAR — Paper Trading Platform: Virtual Portfolio
========================================================
Combines PaperAccount, PaperOrderManager, and PaperPositionManager into a unified portfolio.
"""

from typing import Dict, List, Any, Optional
from paper_trading.paper_account import PaperAccount
from paper_trading.paper_order_manager import PaperOrderManager
from paper_trading.paper_positions import PaperPositionManager
from paper_trading.paper_models import PaperAccountSummary, PaperPosition, PaperOrder


class PaperPortfolio:
    """
    Virtual Portfolio Coordinator.
    """

    def __init__(self, initial_capital: float = 1000000.0):
        self.account = PaperAccount(initial_capital)
        self.order_manager = PaperOrderManager()
        self.position_manager = PaperPositionManager()

    def place_paper_order(
        self,
        symbol: str,
        action: str,
        order_type: str,
        quantity: int,
        price: float = 0.0,
        stop_price: float = 0.0,
        stop_loss: float = 0.0,
        target_1: float = 0.0,
        target_2: float = 0.0,
        target_3: float = 0.0,
        strategy: str = "SWING",
        confidence: float = 0.0
    ) -> Dict[str, Any]:
        """Places a paper order, checks margin, and opens position if filled."""
        margin_required = (price if price > 0 else 100.0) * quantity * 0.20  # 20% margin
        if not self.account.allocate_margin(margin_required):
            return {"success": False, "reason": "Insufficient Virtual Margin"}

        order = self.order_manager.create_order(
            symbol=symbol, action=action, order_type=order_type,
            quantity=quantity, price=price, stop_price=stop_price,
            strategy=strategy, confidence=confidence
        )

        pos = None
        if order.status == "FILLED":
            pos = self.position_manager.open_position(
                symbol=symbol, action=action, quantity=quantity,
                entry_price=order.filled_price, stop_loss=stop_loss,
                target_1=target_1, target_2=target_2, target_3=target_3,
                strategy=strategy, ai_confidence=confidence
            )

        return {
            "success": True,
            "order_id": order.order_id,
            "status": order.status,
            "filled_price": order.filled_price,
            "position_id": pos.position_id if pos else None
        }

    def close_paper_position(self, position_id: str, exit_price: float) -> Optional[Dict[str, Any]]:
        """Closes position, releases margin, and updates account realized P&L."""
        res = self.position_manager.close_position(position_id, exit_price)
        if res:
            margin_released = res["entry_price"] * res["quantity"] * 0.20
            self.account.release_margin(margin_released)
            self.account.update_pnl(realized=res["realized_pnl"])
        return res

    def update_market_prices(self, price_map: Dict[str, float]):
        """Updates prices for all open positions and updates account unrealized P&L."""
        for sym, px in price_map.items():
            self.position_manager.update_market_price(sym, px)

        total_unrealized = sum(p.current_pnl for p in self.position_manager.get_open_positions())
        self.account.update_pnl(realized=0.0, unrealized=total_unrealized)

    def get_summary(self) -> Dict[str, Any]:
        acc = self.account.get_summary()
        open_positions = [p.__dict__ for p in self.position_manager.get_open_positions()]

        return {
            "account": acc.__dict__,
            "open_positions": open_positions,
            "open_positions_count": len(open_positions)
        }
