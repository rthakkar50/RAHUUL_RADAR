import os
import sys
import unittest
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(BASE_DIR))

from core.telegram_service import TelegramService
from core.telegram_intelligence import TelegramIntelligence

class TestSprint189CommandCenter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = TelegramService.get_instance()
        cls.intel = TelegramIntelligence.get_instance()

    def test_01_enterprise_dashboard(self):
        dash = self.intel.get_enterprise_dashboard()
        self.assertIn("ENTERPRISE DASHBOARD", dash)
        self.assertIn("SYSTEM STATUS", dash)
        self.assertIn("MARKET REGIME", dash)
        self.assertIn("SCANNER STATS", dash)
        self.assertIn("PORTFOLIO", dash)

    def test_02_paper_trade_commands(self):
        trade_res = self.intel.execute_paper_trade_cmd("RELIANCE.NS", "BUY")
        self.assertIn("PAPER TRADE EXECUTED", trade_res)
        self.assertIn("RELIANCE.NS", trade_res)

        close_res = self.intel.close_paper_trade_cmd("RELIANCE.NS")
        self.assertIn("PAPER POSITION CLOSED", close_res)
        self.assertIn("RELIANCE.NS", close_res)

    def test_03_watchlist_management(self):
        add_res = self.intel.add_to_watchlist("INFY.NS")
        self.assertIn("Added `INFY.NS` to your Unlimited Watchlist", add_res)

        watchlist_rep = self.intel.get_watchlist_report()
        self.assertIn("INFY.NS", watchlist_rep)

        rem_res = self.intel.remove_from_watchlist("INFY.NS")
        self.assertIn("Removed `INFY.NS` from Watchlist", rem_res)

    def test_04_scheduled_reports(self):
        m = self.intel.generate_morning_report()
        self.assertIn("MORNING MARKET REPORT", m)

        mid = self.intel.generate_midday_report()
        self.assertIn("MIDDAY MARKET REPORT", mid)

        eod = self.intel.generate_eod_report()
        self.assertIn("END OF DAY MARKET REPORT", eod)

    def test_05_portfolio_and_risk_control(self):
        cash = self.intel.get_cash_report()
        self.assertIn("CASH & MARGIN", cash)

        eq = self.intel.get_equity_report()
        self.assertIn("TOTAL EQUITY", eq)

        exp = self.intel.get_exposure_report()
        self.assertIn("CAPITAL EXPOSURE", exp)

        sec = self.intel.get_sector_report()
        self.assertIn("SECTOR ALLOCATION", sec)

        risk = self.intel.get_risk_report()
        self.assertIn("RISK CENTER METRICS", risk)

    def test_06_admin_and_notification_settings(self):
        admin = self.intel.get_admin_report()
        self.assertIn("SYSTEM ADMIN COMMAND CENTER", admin)

        notif = self.intel.get_notification_settings_report()
        self.assertIn("NOTIFICATION CENTER SETTINGS", notif)

    def test_07_state_change_detection(self):
        status1 = self.service.run_heartbeat_check()
        self.assertIn("ts", status1)
        # Re-run immediately - no state change alert
        status2 = self.service.run_heartbeat_check()
        self.assertEqual(status1["api"], status2["api"])

    def test_08_stress_test_1000_commands(self):
        start_t = time.time()
        for i in range(1000):
            self.service.audit_command("123456", f"/stress_cmd_{i}", 0.5, True, "", 50)
            if i % 100 == 0:
                self.intel.get_copilot_analysis("TCS")
        duration = time.time() - start_t
        self.assertLess(duration, 10.0)

if __name__ == "__main__":
    unittest.main()
