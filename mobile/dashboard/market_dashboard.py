"""
RAHUUL RADAR — Mobile Dashboard: Market Dashboard Home View (Task 1)
====================================================================
Renders Market Status, Account Status, Portfolio Value, Today's P&L,
Open Positions, Risk Utilization, and AI Signals.
"""

from typing import Dict, Any
from mobile.dashboard.dashboard_controller import DashboardController


class MarketDashboardView:
    """
    Renders Home Dashboard screen layout model.
    """

    def __init__(self, controller: DashboardController = None):
        self.controller = controller or DashboardController()

    def render(self) -> Dict[str, Any]:
        """Renders Home Dashboard state model."""
        data = self.controller.get_home_dashboard()
        return {
            "screen": "MARKET_DASHBOARD_HOME",
            "widgets": [
                {"type": "MARKET_BANNER", "data": data["market_status"]},
                {"type": "ACCOUNT_SUMMARY", "data": data["account_status"]},
                {"type": "PORTFOLIO_KPI", "data": data["portfolio"]},
                {"type": "RISK_METER", "data": data["risk_utilization"]},
                {"type": "AI_SIGNALS_CAROUSEL", "data": data["latest_ai_signals"]}
            ],
            "render_time_ms": data["load_time_ms"]
        }
