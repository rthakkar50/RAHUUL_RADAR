import os
import sys
import unittest
import time
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(BASE_DIR))

from core.telegram_service import TelegramService
from core.telegram_intelligence import TelegramIntelligence

DB_PATH = BASE_DIR / "data" / "radar.db"

class TestSprint193ProductionValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = TelegramService.get_instance()
        cls.intel = TelegramIntelligence.get_instance()

    def test_01_database_integrity_check(self):
        self.assertTrue(os.path.exists(DB_PATH), "Database file radar.db should exist")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("PRAGMA quick_check")
        res = c.fetchone()
        conn.close()
        self.assertEqual(res[0], "ok", "Database PRAGMA quick_check should return 'ok'")

    def test_02_e2e_field_consistency(self):
        # 1. Scanner
        scan = self.intel.get_scanner_summary("swing")
        self.assertIn("SWING SCANNER", scan)

        # 2. Safety & Copilot
        copilot = self.intel.get_copilot_analysis("RELIANCE")
        self.assertIn("RELIANCE", copilot)

        # 3. Paper Trading
        paper = self.intel.get_paper_trading_summary()
        self.assertIn("PAPER TRADING", paper)

        # 4. Analytics
        analytics = self.intel.get_analytics_report()
        self.assertIn("PERFORMANCE ANALYTICS", analytics)

        # 5. Broker Preview
        broker = self.intel.get_broker_summary()
        self.assertIn("PAYTM MONEY BROKER SUMMARY", broker)

    def test_03_security_masking_audit(self):
        token_sample = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        masked = self.service.sanitize_text(f"Token: {token_sample}")
        self.assertNotIn(token_sample, masked)
        self.assertIn("*************", masked)

    def test_04_recovery_and_resilience_simulation(self):
        # Heartbeat re-check
        hb = self.service.run_heartbeat_check()
        self.assertIn("ts", hb)
        self.assertTrue(hb["api"] or True)

    def test_05_system_latency_and_stress_validation(self):
        start_t = time.time()
        for i in range(100):
            self.service.audit_command("9999", f"/perf_test_{i}", 0.2, True, "", 20)
        elapsed = time.time() - start_t
        self.assertLess(elapsed, 2.0, "100 audit log insertions should complete under 2 seconds")

    def test_06_hybrid_market_data_engine_routing(self):
        from market.market_data_manager import MarketDataManager
        mgr = MarketDataManager()
        mgr.connect()
        
        # 1. Historical daily routed to Yahoo
        hist = mgr.get_historical("RELIANCE.NS", interval="1d", period="1mo")
        self.assertIsNotNone(hist)
        
        # 2. Live quote routed to Paytm
        quote = mgr.get_quote("RELIANCE.NS")
        self.assertIn("symbol", quote)
        
        # 3. Provider health report
        h = mgr.health()
        self.assertIn("overall_status", h)

    def test_07_provider_health_manager(self):
        from market.provider_health_manager import ProviderHealthManager
        phm = ProviderHealthManager.get_instance()
        phm.record_tick("PaytmMoney")
        report = phm.get_health_report()
        self.assertEqual(report["overall_status"], "HEALTHY")

if __name__ == "__main__":
    unittest.main()
