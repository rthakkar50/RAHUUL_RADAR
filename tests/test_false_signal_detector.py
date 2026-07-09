import sys
import os
import unittest

# Ensure the root folder is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.false_signal_detector import FalseSignalDetector

class TestFalseSignalDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.detector = FalseSignalDetector()
        
    def test_approved_signal(self) -> None:
        """Test Case 1: All indicators align perfectly with the proposed signal."""
        data = {
            "Trend": "BULL",
            "Volume": "HIGH",
            "Market Regime": "TRENDING",
            "Sector Rotation": "STRONG",
            "Relative Strength": "STRONG",
            "Option Chain": "BULLISH"
        }
        res = self.detector.detect(data, "BUY")
        self.assertEqual(res["status"], "APPROVED")
        self.assertEqual(len(res["reasons"]), 0)
        
    def test_rejected_signal(self) -> None:
        """Test Case 2: Broad invalidation across multiple engines."""
        data = {
            "Trend": "BEAR",
            "Volume": "LOW",
            "Market Regime": "CHOPPY",
            "Sector Rotation": "WEAK",
            "Relative Strength": "WEAK",
            "Option Chain": "BEARISH"
        }
        res = self.detector.detect(data, "BUY")
        self.assertEqual(res["status"], "REJECTED")
        self.assertGreaterEqual(len(res["reasons"]), 5)
        
    def test_missing_trend(self) -> None:
        """Test Case 3: Missing trend defaults to UNKNOWN, which shouldn't falsely reject on its own."""
        data = {
            "Volume": "HIGH",
            "Market Regime": "TRENDING",
            "Sector Rotation": "STRONG",
            "Relative Strength": "STRONG",
            "Option Chain": "BULLISH"
        }
        res = self.detector.detect(data, "BUY")
        self.assertEqual(res["status"], "APPROVED")
        
    def test_weak_volume(self) -> None:
        """Test Case 4: Trade rejected specifically due to volume mismatch."""
        data = {
            "Trend": "BULL",
            "Volume": "LOW",
            "Market Regime": "TRENDING",
            "Sector Rotation": "STRONG",
            "Relative Strength": "STRONG",
            "Option Chain": "BULLISH"
        }
        res = self.detector.detect(data, "BUY")
        self.assertEqual(res["status"], "REJECTED")
        self.assertIn("Volume confirmation failure: Low volume.", res["reasons"])
        
    def test_weak_sector(self) -> None:
        """Test Case 5: Trade rejected due to weak underlying sector strength."""
        data = {
            "Trend": "BULL",
            "Volume": "HIGH",
            "Market Regime": "TRENDING",
            "Sector Rotation": "WEAK",
            "Relative Strength": "STRONG",
            "Option Chain": "BULLISH"
        }
        res = self.detector.detect(data, "BUY")
        self.assertEqual(res["status"], "REJECTED")
        self.assertTrue(any("Sector strength failure" in r for r in res["reasons"]))
        
    def test_option_chain_conflict(self) -> None:
        """Test Case 6: Trade rejected due to derivatives conflict (buying into a bearish chain)."""
        data = {
            "Trend": "BULL",
            "Volume": "HIGH",
            "Market Regime": "TRENDING",
            "Sector Rotation": "STRONG",
            "Relative Strength": "STRONG",
            "Option Chain": "BEARISH"
        }
        res = self.detector.detect(data, "BUY")
        self.assertEqual(res["status"], "REJECTED")
        self.assertTrue(any("Option chain confirmation failure" in r for r in res["reasons"]))

if __name__ == '__main__':
    unittest.main()
