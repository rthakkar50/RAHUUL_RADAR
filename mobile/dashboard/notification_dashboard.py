"""
RAHUUL RADAR — Mobile Dashboard: Notifications & Settings View (Task 6 & Task 7)
================================================================================
Renders Notifications Center and App Settings Configuration.
"""

from typing import Dict, Any
from mobile.dashboard.dashboard_controller import DashboardController


class NotificationDashboardView:
    """
    Renders Notifications Center and Settings screen layout models.
    """

    def __init__(self, controller: DashboardController = None):
        self.controller = controller or DashboardController()

    def render_notifications(self) -> Dict[str, Any]:
        """Task 6: Renders Notifications Center."""
        data = self.controller.get_notifications_dashboard()
        return {
            "screen": "NOTIFICATIONS_CENTER",
            "categories": ["ALL", "AI_SIGNALS", "RISK_ALERTS", "MARGIN_ALERTS", "EXECUTION_ALERTS"],
            "items": data["notifications"],
            "render_time_ms": data["load_time_ms"]
        }

    def render_settings(self) -> Dict[str, Any]:
        """Task 7: Renders Settings screen."""
        settings = self.controller.get_settings()
        return {
            "screen": "APP_SETTINGS",
            "sections": [
                {"title": "Theme", "current": settings["theme"], "options": ["DARK_PRO", "LIGHT", "SYSTEM"]},
                {"title": "Broker", "current": settings["broker"], "status": "CONNECTED"},
                {"title": "Scanner Mode", "current": settings["scanner_mode"], "options": ["SWING", "FNO", "ALL"]},
                {"title": "Notifications", "enabled": settings["notifications_enabled"]},
                {"title": "AI Engine Settings", "current": settings["ai_mode"]}
            ]
        }
