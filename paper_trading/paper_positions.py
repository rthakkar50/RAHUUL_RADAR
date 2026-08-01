"""
RAHUUL RADAR — Paper Trading Platform: Position Manager (Task 3)
=================================================================
Tracks virtual open positions, partial exits, trailing stop adjustments,
average entry price, holding time, and unrealized P&L.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from paper_trading.paper_models import PaperPosition


class PaperPositionManager:
    """
    Virtual Position Lifecycle Manager.
    """

    def __init__(self):
        self._positions: Dict[str, PaperPosition] = {}

    def open_position(
        self,
        symbol: str,
        action: str,
        quantity: int,
        entry_price: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        target_3: float,
        strategy: str = "SWING",
        ai_confidence: float = 0.0
    ) -> PaperPosition:
        """Opens a new virtual position or averages into an existing position."""
        now_str = datetime.now().isoformat()
        pos_key = f"{symbol.upper()}:{action.upper()}"

        if pos_key in self._positions:
            # Average Price & Quantity addition
            pos = self._positions[pos_key]
            total_qty = pos.quantity + quantity
            avg_price = ((pos.entry_price * pos.quantity) + (entry_price * quantity)) / total_qty
            pos.quantity = total_qty
            pos.entry_price = round(avg_price, 2)
            pos.current_price = entry_price
            return pos

        pos_id = f"POS-{uuid.uuid4().hex[:8].upper()}"
        pos = PaperPosition(
            position_id=pos_id,
            symbol=symbol.upper(),
            action=action.upper(),
            quantity=quantity,
            entry_price=entry_price,
            current_price=entry_price,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            target_3=target_3,
            trailing_stop=stop_loss,
            current_pnl=0.0,
            pnl_pct=0.0,
            open_time=now_str,
            holding_mins=0,
            strategy=strategy,
            ai_confidence=ai_confidence
        )
        self._positions[pos_key] = pos
        return pos

    def update_market_price(self, symbol: str, current_price: float):
        """Updates current price and unrealized P&L for open positions."""
        for pos in self._positions.values():
            if pos.symbol == symbol.upper():
                pos.current_price = current_price
                diff = (current_price - pos.entry_price) if pos.action == "BUY" else (pos.entry_price - current_price)
                pos.current_pnl = round(diff * pos.quantity, 2)
                pos.pnl_pct = round((diff / max(pos.entry_price, 1e-6)) * 100.0, 2)

    def partial_exit(self, position_id: str, exit_qty: int, exit_price: float) -> Optional[Dict[str, Any]]:
        """Executes partial position exit."""
        for key, pos in list(self._positions.items()):
            if pos.position_id == position_id:
                if exit_qty >= pos.quantity:
                    return self.close_position(position_id, exit_price)

                # Realized P&L for partial quantity
                diff = (exit_price - pos.entry_price) if pos.action == "BUY" else (pos.entry_price - exit_price)
                realized_pnl = round(diff * exit_qty, 2)
                pos.quantity -= exit_qty

                return {
                    "position_id": position_id,
                    "closed_qty": exit_qty,
                    "remaining_qty": pos.quantity,
                    "realized_pnl": realized_pnl,
                    "is_fully_closed": False
                }
        return None

    def close_position(self, position_id: str, exit_price: float) -> Optional[Dict[str, Any]]:
        """Closes position completely."""
        for key, pos in list(self._positions.items()):
            if pos.position_id == position_id:
                diff = (exit_price - pos.entry_price) if pos.action == "BUY" else (pos.entry_price - exit_price)
                realized_pnl = round(diff * pos.quantity, 2)
                return_pct = round((diff / max(pos.entry_price, 1e-6)) * 100.0, 2)

                del self._positions[key]

                return {
                    "position_id": position_id,
                    "symbol": pos.symbol,
                    "action": pos.action,
                    "quantity": pos.quantity,
                    "entry_price": pos.entry_price,
                    "exit_price": exit_price,
                    "realized_pnl": realized_pnl,
                    "return_pct": return_pct,
                    "is_fully_closed": True,
                    "strategy": pos.strategy,
                    "ai_confidence": pos.ai_confidence
                }
        return None

    def update_trailing_stop(self, position_id: str, new_trailing_stop: float):
        """Updates trailing stop level."""
        for pos in self._positions.values():
            if pos.position_id == position_id:
                pos.trailing_stop = new_trailing_stop

    def get_open_positions(self) -> List[PaperPosition]:
        return list(self._positions.values())
