import os
import sys
import unittest
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(BASE_DIR))

from core.telegram_service import TelegramService
from core.telegram_intelligence import TelegramIntelligence

class TestSprint188TelegramPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = TelegramService.get_instance()
        cls.intel = TelegramIntelligence.get_instance()

    def test_01_service_initialization_and_loggers(self):
        self.assertIsNotNone(self.service)
        self.assertTrue((BASE_DIR / "logs" / "telegram.log").exists())
        self.assertTrue((BASE_DIR / "logs" / "telegram_error.log").exists())

    def test_02_token_masking_security(self):
        text_with_token = "access_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.secret123.sig and telegram_bot_token: 8805672111:AAEBsy0L4Za7hb"
        sanitized = self.service.sanitize_text(text_with_token)
        self.assertNotIn("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", sanitized)
        self.assertNotIn("8805672111", sanitized)
        self.assertIn("*************", sanitized)

    def test_03_command_audit_logging(self):
        self.service.audit_command("12345", "/test_cmd", 15.5, True, "", 100)
        self.assertTrue((BASE_DIR / "logs" / "telegram_commands.log").exists())

    def test_04_retry_queue_enqueue(self):
        self.service.enqueue_retry_message("12345", "Test alert queue message")
        # Try processing queue
        self.service.process_retry_queue("mock_token")

    def test_05_heartbeat_check(self):
        hb = self.service.run_heartbeat_check()
        self.assertIn("ts", hb)
        self.assertIn("api", hb)

    def test_06_intelligence_commands(self):
        health = self.intel.get_system_health()
        self.assertIn("SYSTEM HEALTH", health)

        diag = self.intel.get_diagnostics_report()
        self.assertIn("ENTERPRISE DIAGNOSTICS", diag)

        ping = self.intel.get_ping_report()
        self.assertIn("PONG", ping)

        help_man = self.intel.get_help_manual()
        self.assertIn("COMMANDS", help_man)

        settings = self.intel.get_settings_summary()
        self.assertIn("SETTINGS SUMMARY", settings)

        token_st = self.intel.get_paytm_status_detailed()
        self.assertIn("PAYTM TOKEN STATUS", token_st)

        scanner_sum = self.intel.get_scanner_summary("swing")
        self.assertIn("SWING SCANNER SUMMARY", scanner_sum)

        copilot = self.intel.get_copilot_analysis("RELIANCE")
        self.assertIn("AI COPILOT ANALYSIS", copilot)

        morning = self.intel.generate_morning_report()
        self.assertIn("MORNING MARKET REPORT", morning)

    def test_07_export_file_generation(self):
        csv_file = self.intel.generate_export_file("csv", "portfolio")
        self.assertTrue(os.path.exists(csv_file))
        self.assertTrue(csv_file.endswith(".csv"))

        json_file = self.intel.generate_export_file("json", "portfolio")
        self.assertTrue(os.path.exists(json_file))
        self.assertTrue(json_file.endswith(".json"))

    def test_08_simulated_stress_test(self):
        start_t = time.time()
        for i in range(100):
            self.service.audit_command("12345", f"/cmd_{i}", 1.2, True, "", 50)
            self.intel.get_copilot_analysis("TCS")
        duration = time.time() - start_t
        self.assertLess(duration, 5.0)

if __name__ == "__main__":
    unittest.main()
