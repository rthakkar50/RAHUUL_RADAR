import time
import unittest
from mobile.dashboard.dashboard_service import DashboardService
from mobile.dashboard.dashboard_controller import DashboardController
from mobile.dashboard.market_dashboard import MarketDashboardView
from mobile.dashboard.portfolio_dashboard import PortfolioDashboardView
from mobile.dashboard.watchlist_dashboard import WatchlistDashboardView
from mobile.dashboard.risk_dashboard import RiskDashboardView
from mobile.dashboard.analytics_dashboard import AnalyticsDashboardView
from mobile.dashboard.notification_dashboard import NotificationDashboardView


class TestMobileDashboard(unittest.TestCase):

    def setUp(self):
        self.service = DashboardService.get_instance()
        self.controller = DashboardController(self.service)
        self.market_view = MarketDashboardView(self.controller)
        self.portfolio_view = PortfolioDashboardView(self.controller)
        self.watchlist_view = WatchlistDashboardView(self.controller)
        self.risk_view = RiskDashboardView(self.controller)
        self.analytics_view = AnalyticsDashboardView(self.controller)
        self.notification_view = NotificationDashboardView(self.controller)

    def test_dashboard_home_screen_and_performance(self):
        """Task 1 & Task 8: Dashboard Home render & <200ms load latency requirement."""
        start_time = time.time()
        home = self.market_view.render()
        elapsed_ms = (time.time() - start_time) * 1000.0

        self.assertLess(elapsed_ms, 200.0, f"Dashboard load time {elapsed_ms:.2f}ms exceeded 200ms target!")
        self.assertEqual(home["screen"], "MARKET_DASHBOARD_HOME")
        self.assertTrue(len(home["widgets"]) >= 4)

    def test_portfolio_dashboard(self):
        """Task 2: Portfolio Dashboard screen render."""
        port = self.portfolio_view.render()
        self.assertEqual(port["screen"], "PORTFOLIO_DASHBOARD")
        self.assertTrue(len(port["widgets"]) >= 3)

    def test_watchlist_dashboard_tabs(self):
        """Task 3: Watchlist Dashboard with Swing, F&O, Intraday tabs."""
        swing_wl = self.watchlist_view.render("SWING")
        self.assertEqual(swing_wl["active_tab"], "SWING")
        self.assertTrue(len(swing_wl["signal_cards"]) > 0)

        fno_wl = self.watchlist_view.render("FNO")
        self.assertEqual(fno_wl["active_tab"], "FNO")
        self.assertTrue(len(fno_wl["signal_cards"]) > 0)

    def test_risk_dashboard(self):
        """Task 4: Risk Dashboard metrics render."""
        risk = self.risk_view.render()
        self.assertEqual(risk["screen"], "RISK_DASHBOARD")
        self.assertTrue(len(risk["widgets"]) >= 4)

    def test_analytics_dashboard(self):
        """Task 5: Analytics Dashboard charts & performance render."""
        analytics = self.analytics_view.render()
        self.assertEqual(analytics["screen"], "ANALYTICS_DASHBOARD")
        self.assertTrue(len(analytics["widgets"]) >= 4)

    def test_notifications_and_settings(self):
        """Task 6 & Task 7: Notifications center & Settings screen."""
        notifs = self.notification_view.render_notifications()
        self.assertEqual(notifs["screen"], "NOTIFICATIONS_CENTER")
        self.assertTrue(len(notifs["items"]) > 0)

        settings = self.notification_view.render_settings()
        self.assertEqual(settings["screen"], "APP_SETTINGS")
        self.assertTrue(len(settings["sections"]) >= 4)


if __name__ == "__main__":
    unittest.main()
