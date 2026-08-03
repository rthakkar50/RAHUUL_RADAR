import unittest
from application.swing_scanner_service import SwingScannerService

class TestSprint165MetricsReconciliation(unittest.TestCase):
    def test_sprint165_scanner_metrics_reconciliation_formulas(self):
        """Verify SPRINT-165 metrics reconciliation formulas."""
        service = SwingScannerService()
        res = service.execute_swing_scan()
        
        tot_universe = res.get("total_universe", 0)
        tot_scanned = res.get("total_scanned", 0)
        qualified = res.get("qualified_count", 0)
        filter_rejected = res.get("filter_rejected_count", 0)
        no_data = res.get("no_data_count", 0)
        rejected = res.get("rejected_count", 0)
        
        # Formula 1: qualified_count + filter_rejected_count == total_scanned
        self.assertEqual(
            qualified + filter_rejected, tot_scanned,
            f"Formula 1 Failure: qualified({qualified}) + filter_rejected({filter_rejected}) != total_scanned({tot_scanned})"
        )
        
        # Formula 2: total_scanned + no_data_count == total_universe
        self.assertEqual(
            tot_scanned + no_data, tot_universe,
            f"Formula 2 Failure: total_scanned({tot_scanned}) + no_data({no_data}) != total_universe({tot_universe})"
        )
        
        # Formula 3: filter_rejected_count + no_data_count == rejected_count
        self.assertEqual(
            filter_rejected + no_data, rejected,
            f"Formula 3 Failure: filter_rejected({filter_rejected}) + no_data({no_data}) != rejected({rejected})"
        )
        
        # Master Identity: total_universe == qualified + filter_rejected + no_data
        self.assertEqual(
            tot_universe, qualified + filter_rejected + no_data,
            "Master Identity Failure: total_universe != qualified + filter_rejected + no_data"
        )

if __name__ == "__main__":
    unittest.main()
