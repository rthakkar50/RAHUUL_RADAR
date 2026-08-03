import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(BASE_DIR))

from core.telegram_intelligence import TelegramIntelligence

class TestSprint191Analytics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.intel = TelegramIntelligence.get_instance()

    def test_01_analytics_report(self):
        rep = self.intel.get_analytics_report()
        self.assertIn("ENTERPRISE PERFORMANCE ANALYTICS", rep)
        self.assertIn("Win Rate", rep)
        self.assertIn("Profit Factor", rep)
        self.assertIn("Expectancy", rep)

    def test_02_strategy_report(self):
        rep = self.intel.get_strategy_report()
        self.assertIn("STRATEGY INTELLIGENCE", rep)
        self.assertIn("Optimal Holding Time", rep)
        self.assertIn("Best Sector", rep)

    def test_03_heatmap_report(self):
        rep = self.intel.get_heatmap_report()
        self.assertIn("SECTOR & SIGNAL HEATMAP", rep)
        self.assertIn("IT / Tech", rep)

    def test_04_replay_report(self):
        rep = self.intel.get_replay_report()
        self.assertIn("RECENT TRADE REPLAY", rep)
        self.assertIn("Validation", rep)

if __name__ == "__main__":
    unittest.main()
