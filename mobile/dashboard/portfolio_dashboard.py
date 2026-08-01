"""
RAHUUL RADAR — Mobile Dashboard: Portfolio Dashboard View (Task 2)
===================================================================
Renders Total Capital, Available Margin, Used Margin, Holdings,
Open Positions, Today's Profit, Total Profit, Winning %, and Drawdown.
"""

from typing import Dict, Any
from mobile.dashboard.dashboard_controller import DashboardController


class PortfolioDashboardView:
    """
    Renders Portfolio Dashboard screen layout model.
    """

    def __init__(self, controller: DashboardController = None):
        self.controller = controller or DashboardController()

    def render(self) -> Dict[str, Any]:
        """Renders Portfolio Dashboard state model."""
        data = self.controller.get_portfolio_dashboard()
        return {
            "screen": "PORTFOLIO_DASHBOARD",
            "widgets": [
                {"type": "CAPITAL_MARGIN_CARD", "data": {
                    "total_capital": data["total_capital"],
                    "available_margin": data["available_margin"],
                    "used_margin": data["used_margin"]
                }},
                {"type": "PNL_PERFORMANCE_CARD", "data": {
                    "portfolio_value": data["portfolio_value"],
                    "todays_pnl": data["todays_pnl"],
                    "total_pnl": data["total_pnl"],
                    "winning_rate": data["winning_rate"],
                    "drawdown": data["drawdown"]
                }},
                {"type": "POSITIONS_AND_HOLDINGS_COUNTER", "data": {
                    "open_positions": data["open_positions_count"],
                    "holdings": data["holdings_count"]
                }}
            ],
            "render_time_ms": data["load_time_ms"]
        }
