"""
RAHUUL RADAR — Phase-1 Limited Live Trading: Order Confirmation Gate
=====================================================================
Pre-trade risk verification and mandatory manual confirmation gate for Phase-1 Live Orders.
"""

from typing import Dict, Any, Optional
from live_trading.capital_manager import CapitalPhaseManager


class LiveOrderGate:
    """
    SRE Pre-Trade Risk Filter & Confirmation Gate.
    """

    def __init__(self, capital_manager: Optional[CapitalPhaseManager] = None):
        self.capital_manager = capital_manager or CapitalPhaseManager()

    def process_order_request(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        stop_loss: float,
        manual_confirmation: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluates pre-trade risk and enforces manual confirmation requirement.
        """
        limits = self.capital_manager.get_current_limits()

        # Rule 1: Manual Confirmation
        if limits.manual_confirmation_required and not manual_confirmation:
            return {
                "allowed": False,
                "reason": "SAFETY GATE: Manual confirmation required before sending order to broker."
            }

        # Rule 2: Risk Limit Check
        sl_pts = abs(price - stop_loss)
        trade_val = price * quantity
        is_risk_ok, risk_reason = self.capital_manager.validate_trade_risk(trade_val, sl_pts, price)

        if not is_risk_ok:
            return {"allowed": False, "reason": risk_reason}

        return {
            "allowed": True,
            "reason": "Risk rules verified and manual confirmation granted.",
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": price
        }
