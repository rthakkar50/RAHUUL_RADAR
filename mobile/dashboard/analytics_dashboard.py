"""
RAHUUL RADAR — Mobile Dashboard: Analytics Dashboard View (Task 5)
==================================================================
Renders Win Rate, Profit Curve, Monthly Returns, Strategy Performance,
Best/Worst Trades, and Average Holding Time.
"""

from typing import Dict, Any
from mobile.dashboard.dashboard_controller import DashboardController


class AnalyticsDashboardView:
    """
    Renders Analytics Dashboard screen layout model.
    """

    def __init__(self, controller: DashboardController = None):
        self.controller = controller or DashboardController()

    def render(self) -> Dict[str, Any]:
        """Renders Analytics Dashboard state model."""
        data = self.controller.get_analytics_dashboard()
        return {
            "screen": "ANALYTICS_DASHBOARD",
            "widgets": [
                {"type": "WIN_RATE_KPI", "data": {"win_rate": data["win_rate"]}},
                {"type": "PROFIT_CURVE_LINE_CHART", "data": {"points": data["profit_curve"]}},
                {"type": "MONTHLY_RETURNS_HEATMAP", "data": data["monthly_returns"]},
                {"type": "STRATEGY_PERFORMANCE_BARS", "data": data["strategy_performance"]},
                {"type": "BEST_WORST_TRADE_CARDS", "data": {
                    "best": data["best_trade"],
                    "worst": data["worst_trade"]
                }},
                {"type": "AVG_HOLDING_TIME_CARD", "data": {"holding_time_mins": data["avg_holding_time_mins"]}}
            ],
            "render_time_ms": data["load_time_ms"]
        }
