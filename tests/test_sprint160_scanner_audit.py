import unittest
import os
import json
from application.swing_scanner_service import SwingScannerService

class TestSprint160ScannerAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = SwingScannerService()
        cls.scan_output = cls.service.execute_swing_scan()

    def test_task1_universe_audit_reconciliation(self):
        """Verify Universe Audit Totals reconcile perfectly."""
        audit = self.scan_output.get("universe_audit", {})
        self.assertIsNotNone(audit, "universe_audit must be present")
        
        configured = audit.get("configured_universe", 0)
        downloaded = audit.get("downloaded_successfully", 0)
        no_candle = audit.get("no_candle_data", 0)
        failed = audit.get("download_failed", 0)
        holiday = audit.get("holiday_symbols", 0)
        timeout = audit.get("timeout", 0)
        invalid = audit.get("invalid_symbols", 0)
        skipped = audit.get("skipped", 0)
        
        # Reconciliation Equation 1: Configured == Sum of all state counts
        sum_components = downloaded + failed + no_candle + holiday + timeout + invalid + skipped
        self.assertEqual(configured, sum_components, f"Universe totals do not reconcile: {configured} != {sum_components}")

        processed = audit.get("final_symbols_processed", 0)
        self.assertEqual(downloaded, processed, "Downloaded must equal final_symbols_processed")

        qualified = audit.get("qualified", 0)
        rejected = audit.get("rejected", 0)
        # Reconciliation Equation 2: Processed == Qualified + Rejected
        self.assertEqual(processed, qualified + rejected, f"Processed totals do not reconcile: {processed} != {qualified} + {rejected}")

        buy = audit.get("buy_count", 0)
        sell = audit.get("sell_count", 0)
        watch = audit.get("watch_count", 0)
        # Reconciliation Equation 3: Qualified == BUY + SELL + WATCH
        self.assertEqual(qualified, buy + sell + watch, f"Qualified totals do not reconcile: {qualified} != {buy}+{sell}+{watch}")

    def test_task2_symbol_status_report(self):
        """Verify every symbol in configured universe has one explicit final status report."""
        report = self.scan_output.get("symbol_status_report", [])
        configured = self.scan_output.get("total_universe", 0)
        self.assertEqual(len(report), configured, "Symbol status report count must equal configured universe")
        
        valid_statuses = {"SUCCESS", "FAILED", "NO DATA", "TIMEOUT", "HOLIDAY", "INVALID", "FILTERED", "QUALIFIED", "REJECTED"}
        for item in report:
            self.assertIn(item["status"], valid_statuses, f"Invalid symbol status for {item['symbol']}: {item['status']}")

    def test_task3_provider_statistics(self):
        """Verify provider statistics for Yahoo and Paytm."""
        stats = self.scan_output.get("provider_statistics", {})
        self.assertIn("yahoo", stats)
        self.assertIn("paytm", stats)
        self.assertGreaterEqual(stats["yahoo"].get("total_requests", 0), 0)

    def test_task4_sell_signal_validation(self):
        """Verify SELL signal validation audit."""
        sell_val = self.scan_output.get("sell_signal_validation", {})
        self.assertEqual(sell_val.get("status"), "VERIFIED_VALID")
        self.assertIn("raw_sell_candidates_generated", sell_val)

    def test_task5_breadth_validation(self):
        """Verify advances, declines, unchanged and breadth ratio reconciliation."""
        bv = self.scan_output.get("breadth_validation", {})
        self.assertTrue(bv.get("reconciled"), "Breadth validation failed reconciliation")

    def test_task6_pipeline_reconciliation(self):
        """Verify pipeline stage counts non-increasing reconciliation."""
        pr = self.scan_output.get("pipeline_reconciliation", {})
        self.assertTrue(pr.get("reconciled"), "Pipeline reconciliation failed")

    def test_task7_csv_generation(self):
        """Verify scanner_audit.csv is generated on disk."""
        self.assertTrue(os.path.exists("data/scanner_audit.csv"), "data/scanner_audit.csv file does not exist")
        with open("data/scanner_audit.csv", "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Symbol,Status,Download", content, "CSV header missing")

if __name__ == "__main__":
    unittest.main()
