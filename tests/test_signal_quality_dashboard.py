import unittest
import json
import os
import csv
from application.signal_quality_service import SignalQualityService
from ui.pages.signal_quality_dashboard import SignalQualityDashboardUI

class TestSignalQualityDashboard(unittest.TestCase):
    def setUp(self):
        self.config_path = "tests/mock_dashboard_quality.json"
        self.export_dir = "tests/mock_exports/"
        
        config_data = {
            "refresh_interval_ms": 5000,
            "gauge_thresholds": {
                "good_min": 75.0,
                "warning_min": 40.0,
                "critical_max": 39.9
            },
            "warning_levels": {
                "memory_warning_mb": 1024.0,
                "cpu_warning_pct": 75.0,
                "latency_warning_ms": 300.0
            },
            "panel_visibility": {
                "panel_1_overall_quality": True,
                "panel_2_confidence": True,
                "panel_3_engine_status": True,
                "panel_4_strategy_ranking": True,
                "panel_5_recent_signals": True,
                "panel_6_market_status": True,
                "panel_7_performance": True,
                "panel_8_validation": True
            },
            "export_settings": {
                "default_export_path": self.export_dir,
                "enable_pdf_export": True,
                "enable_csv_export": True
            }
        }
        with open(self.config_path, "w") as f:
            json.dump(config_data, f)
            
        self.service = SignalQualityService(config_path=self.config_path)
        self.ui = SignalQualityDashboardUI(self.service)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        # Cleanup mock exports if they exist
        if os.path.exists(self.export_dir):
            for file in os.listdir(self.export_dir):
                os.remove(os.path.join(self.export_dir, file))
            os.rmdir(self.export_dir)

    def test_dashboard_load(self):
        # UI is initialized with 8 panels
        rendered = self.ui.render()
        self.assertEqual(len(rendered), 8)
        self.assertTrue("Panel 1: Overall Signal Quality" in rendered)

    def test_refresh_and_update(self):
        mock_data = {
            "confidence_score": 85.0,
            "recent_signals": [{"symbol": "NIFTY", "action": "BUY"}],
            "top_strategy": "MomentumBreakout",
            "market_status": "Bullish",
            "performance": {"latency_ms": 100.0, "memory_mb": 500.0, "cpu_pct": 30.0},
            "validation": {"walk_forward_status": "PASSED", "institution_score": 90.0},
            "engines_health": {"trend": True, "momentum": True}
        }
        
        fresh_summary = self.service.refresh_dashboard(mock_data)
        
        # Calculate expected overall quality:
        # Confidence = 85.0, Val = 90.0. Base = (85+90)/2 = 87.5. No penalties.
        self.assertEqual(fresh_summary["overall_quality"], 87.5)
        self.assertEqual(fresh_summary["health_status"], "GREEN")
        
        # UI update
        self.ui.update_data(fresh_summary)
        self.assertEqual(self.ui.get_panel_state("Panel 1: Overall Signal Quality"), 87.5)
        self.assertEqual(self.ui.get_panel_state("Panel 4: Top Ranked Strategy"), "MomentumBreakout")

    def test_penalties_and_health(self):
        mock_data = {
            "confidence_score": 50.0,
            "recent_signals": [],
            "top_strategy": "None",
            "market_status": "Volatile",
            "performance": {"latency_ms": 500.0, "memory_mb": 2000.0, "cpu_pct": 95.0},
            "validation": {"walk_forward_status": "FAILED", "institution_score": 10.0},
            "engines_health": {"trend": False, "momentum": False, "volume": True} # 2/3 failed -> RED
        }
        
        summary = self.service.refresh_dashboard(mock_data)
        # Base = (50+10)/2 = 30. Penalties: latency=10, mem=10, cpu=10. Final = 0 (clamped)
        self.assertEqual(summary["overall_quality"], 0.0)
        self.assertEqual(summary["health_status"], "RED")

    def test_empty_data(self):
        summary = self.service.refresh_dashboard({})
        self.assertEqual(summary["overall_quality"], 0.0)
        self.assertEqual(summary["health_status"], "RED")
        
        self.ui.update_data(summary)
        self.assertEqual(self.ui.get_panel_state("Panel 1: Overall Signal Quality"), 0.0)

    def test_export_json_csv(self):
        mock_data = self.service.refresh_dashboard() # Get default mock data
        
        # Test JSON
        filepath_json = self.service.export_dashboard(mock_data, format_type="JSON")
        self.assertTrue(os.path.exists(filepath_json))
        with open(filepath_json, "r") as f:
            data = json.load(f)
            self.assertEqual(data["health_status"], "GREEN")
            
        # Test CSV
        filepath_csv = self.service.export_dashboard(mock_data, format_type="CSV")
        self.assertTrue(os.path.exists(filepath_csv))
        with open(filepath_csv, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertTrue(len(rows) > 5)
            self.assertEqual(rows[0], ["Metric", "Value"])

if __name__ == '__main__':
    unittest.main()
