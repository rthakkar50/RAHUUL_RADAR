import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(BASE_DIR))

from core.telegram_intelligence import TelegramIntelligence

class TestSprint192BrokerAdapter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.intel = TelegramIntelligence.get_instance()

    def test_01_broker_summary(self):
        summary = self.intel.get_broker_summary()
        self.assertIn("PAYTM MONEY BROKER SUMMARY", summary)
        self.assertIn("PREVIEW ONLY", summary)

    def test_02_broker_funds(self):
        funds = self.intel.get_broker_funds()
        self.assertIn("PAYTM MONEY FUNDS", funds)
        self.assertIn("Available Cash", funds)

    def test_03_broker_holdings(self):
        holdings = self.intel.get_broker_holdings()
        self.assertIn("PAYTM MONEY HOLDINGS", holdings)
        self.assertIn("RELIANCE.NS", holdings)

    def test_04_broker_order_preview(self):
        preview = self.intel.get_broker_order_preview("RELIANCE.NS")
        self.assertIn("PAYTM MONEY ORDER PREVIEW", preview)
        self.assertIn("PREVIEW ONLY - NO LIVE EXECUTION", preview)
        self.assertIn("Required Margin", preview)
        self.assertIn("Estimated Charges", preview)

if __name__ == "__main__":
    unittest.main()
