"""
RAHUUL RADAR — Phase-1 Limited Live Trading: Capital & Phase Risk Manager
==========================================================================
Enforces capital limits and maximum risk rules for Phase-1 (₹10k), Phase-2 (₹25k), and Phase-3 (₹50k).
"""

from typing import Dict, Any, Optional
from live_trading.live_models import CapitalPhaseLimits


class CapitalPhaseManager:
    """
    Capital Preservation & Phase Progression Manager.
    """

    def __init__(self, initial_phase: str = "Phase-1"):
        self.current_phase_name = initial_phase
        self.phase_limits = {
            "Phase-1": CapitalPhaseLimits(
                phase_name="Phase-1",
                capital_balance=10000.0,
                max_risk_per_trade_pct=0.5,
                max_daily_loss_pct=1.0,
                max_weekly_loss_pct=3.0,
                manual_confirmation_required=True
            ),
            "Phase-2": CapitalPhaseLimits(
                phase_name="Phase-2",
                capital_balance=25000.0,
                max_risk_per_trade_pct=0.75,
                max_daily_loss_pct=1.5,
                max_weekly_loss_pct=4.0,
                manual_confirmation_required=True
            ),
            "Phase-3": CapitalPhaseLimits(
                phase_name="Phase-3",
                capital_balance=50000.0,
                max_risk_per_trade_pct=1.0,
                max_daily_loss_pct=2.0,
                max_weekly_loss_pct=5.0,
                manual_confirmation_required=False
            )
        }

    def get_current_limits(self) -> CapitalPhaseLimits:
        return self.phase_limits[self.current_phase_name]

    def validate_trade_risk(self, position_size: float, stop_loss_pts: float, price: float) -> Tuple[bool, str]:
        """Validates that order risk does not exceed Phase limit (0.5% for Phase-1 = ₹50 max risk)."""
        limits = self.get_current_limits()
        max_allowed_risk_amount = (limits.capital_balance * limits.max_risk_per_trade_pct) / 100.0
        calculated_trade_risk = (stop_loss_pts / max(price, 1e-6)) * position_size

        if calculated_trade_risk > max_allowed_risk_amount:
            return False, f"Trade risk ₹{calculated_trade_risk:.2f} exceeds Phase-1 limit ₹{max_allowed_risk_amount:.2f} (0.5%)"
        return True, "Risk validation passed"
