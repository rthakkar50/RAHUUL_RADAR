"""
RAHUUL RADAR — Mobile Dashboard: Risk Dashboard View (Task 4)
=============================================================
Renders Risk % Meter, Daily Loss, Max Loss, Margin Used %,
Sector Exposure, and Lot Exposure.
"""

from typing import Dict, Any
from mobile.dashboard.dashboard_controller import DashboardController


class RiskDashboardView:
    """
    Renders Risk Dashboard screen layout model.
    """

    def __init__(self, controller: DashboardController = None):
        self.controller = controller or DashboardController()

    def render(self) -> Dict[str, Any]:
        """Renders Risk Dashboard state model."""
        data = self.controller.get_risk_dashboard()
        return {
            "screen": "RISK_DASHBOARD",
            "widgets": [
                {"type": "RISK_METER_GAUGE", "data": {
                    "current_risk_pct": data["current_risk_pct"],
                    "risk_level": data["risk_level"]
                }},
                {"type": "DAILY_LOSS_LIMIT_CARD", "data": {
                    "daily_loss": data["daily_loss"],
                    "max_daily_loss": data["max_daily_loss"]
                }},
                {"type": "MARGIN_USED_PROGRESS", "data": {
                    "margin_used_pct": data["margin_used_pct"]
                }},
                {"type": "SECTOR_EXPOSURE_PIE", "data": data["sector_exposure"]},
                {"type": "LOT_EXPOSURE_BAR", "data": data["lot_exposure"]}
            ],
            "render_time_ms": data["load_time_ms"]
        }
