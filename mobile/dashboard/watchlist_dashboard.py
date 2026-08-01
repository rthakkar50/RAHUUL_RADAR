"""
RAHUUL RADAR — Mobile Dashboard: Watchlist Dashboard View (Task 3)
==================================================================
Renders tabbed Watchlists (Swing, F&O, Intraday) with detailed AI signal cards.
"""

from typing import Dict, Any
from mobile.dashboard.dashboard_controller import DashboardController


class WatchlistDashboardView:
    """
    Renders Watchlist Dashboard screen layout model.
    """

    def __init__(self, controller: DashboardController = None):
        self.controller = controller or DashboardController()

    def render(self, category: str = "SWING") -> Dict[str, Any]:
        """Renders Watchlist Dashboard state model."""
        data = self.controller.get_watchlist_dashboard(category)
        return {
            "screen": "WATCHLIST_DASHBOARD",
            "active_tab": category.upper(),
            "available_tabs": ["SWING", "FNO", "INTRADAY"],
            "signal_cards": data["items"],
            "render_time_ms": data["load_time_ms"]
        }
