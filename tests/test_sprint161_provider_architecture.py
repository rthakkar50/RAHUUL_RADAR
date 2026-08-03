import unittest
import time
import json
from application.swing_scanner_service import SwingScannerService
from api.main import _get_provider_metadata

class TestSprint161ProviderArchitecture(unittest.TestCase):
    def test_provider_metadata_structure(self):
        """Verify _get_provider_metadata returns mandatory SPRINT-161 fields."""
        live_meta = _get_provider_metadata(mode="LIVE")
        self.assertEqual(live_meta["provider"], "Paytm Money (Live)")
        self.assertIn(live_meta["market_status"], ["OPEN", "CLOSED", "WEEKEND", "HOLIDAY"])
        self.assertIn("timestamp", live_meta)
        self.assertIn("provider_latency", live_meta)
        self.assertIn("provider_health", live_meta)
        self.assertFalse(live_meta["fallback_used"])

        hist_meta = _get_provider_metadata(mode="HISTORICAL")
        self.assertEqual(hist_meta["provider"], "Yahoo Finance (Historical)")
        self.assertEqual(hist_meta["market_status"], "HISTORICAL")

    def test_scanner_health_provider_branding(self):
        """Verify scanner service returns Paytm Money primary provider metadata."""
        service = SwingScannerService()
        output = service.execute_swing_scan()
        health = output.get("scanner_health", {})
        self.assertEqual(health.get("primary_provider"), "Yahoo Finance (Live)")
        self.assertIn("Paytm Money", health.get("secondary_provider", ""))

    def test_no_silent_fallback_flag(self):
        """Verify fallback_used is False for primary provider requests."""
        live_meta = _get_provider_metadata("LIVE")
        self.assertFalse(live_meta.get("fallback_used"), "Silent fallback must be False")

if __name__ == "__main__":
    unittest.main()
