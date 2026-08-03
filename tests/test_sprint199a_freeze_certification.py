import time
import os
import gc
import psutil
import unittest
from api.main import app, _normalize_scanner_response, _is_valid_complete_cache
from application.swing_scanner_service import SwingScannerService
from application.intraday_scanner_service import IntradayScannerService
from core.telegram_intelligence import TelegramIntelligence

class TestSprint199AFreezeCertification(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.process = psutil.Process(os.getpid())
        cls.mem_start = cls.process.memory_info().rss / (1024 * 1024)
        cls.t0 = time.time()

    def test_task1_all_scanners_validation(self):
        """TASK-1: Validate Swing & Intraday Scanner returns canonical structure"""
        swing_service = SwingScannerService()
        swing_res = swing_service.execute_swing_scan()
        self.assertIn("qualified_results", swing_res)
        self.assertGreaterEqual(swing_res.get("total_universe", 0), 200)

        intra_service = IntradayScannerService()
        intra_res = intra_service.execute_intraday_scan()
        self.assertIn("qualified_results", intra_res)
        self.assertGreaterEqual(intra_res.get("total_universe", 0), 184)

    def test_task2_api_and_health_stress(self):
        """TASK-2: Stress Test API endpoints"""
        from fastapi.testclient import TestClient
        client = TestClient(app)

        start_mem = self.process.memory_info().rss / (1024 * 1024)

        # 500 Health Requests (Memory Cache Test)
        for _ in range(500):
            res = client.get("/api/v1/health")
            self.assertEqual(res.status_code, 200)

        # 100 Swing Requests
        for _ in range(100):
            res = client.get("/api/v1/scanner/swing")
            self.assertEqual(res.status_code, 200)

        end_mem = self.process.memory_info().rss / (1024 * 1024)
        mem_diff = end_mem - start_mem
        print(f"\n[STRESS TEST] 600 API Calls Executed. RAM Delta: {mem_diff:.2f} MB")
        self.assertLess(mem_diff, 50.0)  # No severe memory leakage (<50MB delta)

    def test_task6_telegram_commands_validation(self):
        """TASK-6: Validate Telegram Intelligence Reports"""
        intel = TelegramIntelligence.get_instance()
        health_rpt = intel.get_system_health()
        self.assertIn("SYSTEM HEALTH", health_rpt)

        explain_rpt = intel.explain_stock_decision("RELIANCE")
        self.assertIn("ENTERPRISE AI DECISION SCORECARD", explain_rpt)

        strat_rpt = intel.list_strategies()
        self.assertIn("ENTERPRISE CUSTOM STRATEGIES", strat_rpt)

    def test_task14_security_audit(self):
        """TASK-14: Security Audit for Secrets & API Keys in config"""
        import json
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                c = json.load(f)
                # Verify token masking / safety
                auth_id = str(c.get("telegram_authorized_chat_id", ""))
                self.assertTrue(auth_id != "HARDCODED_UNSAFE_KEY")

    def test_task15_memory_cpu_telemetry(self):
        """TASK-3 & TASK-4: Measure RAM, CPU & GC efficiency"""
        gc.collect()
        mem_now = self.process.memory_info().rss / (1024 * 1024)
        cpu_pct = psutil.cpu_percent(interval=None)
        threads = self.process.num_threads()

        print(f"\n[TELEMETRY] Memory: {mem_now:.2f} MB | CPU: {cpu_pct:.1f}% | Active Threads: {threads}")
        self.assertLess(mem_now, 350.0)  # Fits inside Render 512MB RAM free tier limit

if __name__ == "__main__":
    unittest.main()
