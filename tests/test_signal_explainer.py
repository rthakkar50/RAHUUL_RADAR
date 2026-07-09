import sys
import os
import json
import unittest

# Ensure the root folder is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.signal_explainer import SignalExplainer

class TestSignalExplainer(unittest.TestCase):
    def setUp(self) -> None:
        self.explainer = SignalExplainer()

    def test_buy_explanation(self) -> None:
        """Test Case 1: Verifies BUY explanation payload structure and summary."""
        data = {
            "decision": "BUY",
            "Weighted Score": 85,
            "confidence": 90,
            "Trend": "BULL",
            "Volume": "HIGH",
            "Sector Rotation": "STRONG"
        }
        res_str = self.explainer.build_explanation(data)
        res = json.loads(res_str)
        self.assertEqual(res["decision"], "BUY")
        self.assertEqual(res["score"], 85)
        self.assertEqual(res["summary"], "High probability trend continuation.")

    def test_sell_explanation(self) -> None:
        """Test Case 2: Verifies SELL explanation payload structure and summary."""
        data = {
            "decision": "SELL",
            "Weighted Score": 82,
            "confidence": 88,
            "Trend": "BEAR",
            "Volume": "HIGH",
            "Sector Rotation": "STRONG"
        }
        res_str = self.explainer.build_explanation(data)
        res = json.loads(res_str)
        self.assertEqual(res["decision"], "SELL")
        self.assertEqual(res["score"], 82)
        self.assertEqual(res["summary"], "High probability breakdown.")

    def test_wait_explanation(self) -> None:
        """Test Case 3: Verifies WATCH/WAIT explanation payload structure and summary."""
        data = {
            "decision": "WATCH",
            "Weighted Score": 50,
            "confidence": 40
        }
        res_str = self.explainer.build_explanation(data)
        res = json.loads(res_str)
        self.assertEqual(res["decision"], "WATCH")
        self.assertEqual(res["summary"], "Standard setup.")

    def test_missing_keys(self) -> None:
        """Test Case 4: Verifies parser handles missing keys gracefully."""
        data = {
            "decision": "BUY"
        }
        res_str = self.explainer.build_explanation(data)
        res = json.loads(res_str)
        self.assertEqual(res["decision"], "BUY")
        self.assertEqual(res["score"], 0)
        self.assertEqual(res["positive"], [])
        self.assertEqual(res["negative"], [])

    def test_empty_dictionary(self) -> None:
        """Test Case 5: Verifies parser handles an empty dictionary input."""
        data = {}
        res_str = self.explainer.build_explanation(data)
        res = json.loads(res_str)
        self.assertEqual(res["decision"], "WATCH")
        self.assertEqual(res["score"], 0)
        self.assertEqual(res["positive"], [])
        self.assertEqual(res["negative"], [])

    def test_confidence_calculation_exists(self) -> None:
        """Test Case 6: Verifies confidence mapping exists in output payload."""
        data = {
            "confidence": 95
        }
        res_str = self.explainer.build_explanation(data)
        res = json.loads(res_str)
        self.assertIn("confidence", res)
        self.assertEqual(res["confidence"], 95)

    def test_positive_reasons_list(self) -> None:
        """Test Case 7: Validates positive reason mapping logic."""
        data = {
            "Trend": "BULL",
            "Volume": "HIGH",
            "Sector Rotation": "LEADING",
            "Option Chain": "CONFIRMED"
        }
        positives = self.explainer.build_positive_reasons(data)
        self.assertIn("Trend is Bullish", positives)
        self.assertIn("Volume Above Average", positives)
        self.assertIn("Sector Strong", positives)
        self.assertIn("Option Chain Confirmed", positives)

    def test_negative_reasons_list(self) -> None:
        """Test Case 8: Validates negative reason mapping logic."""
        data = {
            "Momentum": "OVERBOUGHT"
        }
        negatives = self.explainer.build_negative_reasons(data)
        self.assertIn("RSI slightly overbought", negatives)
        
        data_numeric = {
            "Momentum": 15
        }
        negatives_num = self.explainer.build_negative_reasons(data_numeric)
        self.assertIn("RSI slightly oversold", negatives_num)

if __name__ == '__main__':
    unittest.main()
