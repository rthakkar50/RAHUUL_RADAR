import unittest
from backtest.historical_data_provider import HistoricalDataProvider

class TestHistoricalDataProvider(unittest.TestCase):
    def test_initialization(self):
        provider = HistoricalDataProvider("2025-01-01", "2025-06-30")
        self.assertEqual(provider.start_date, "2025-01-01")
        self.assertTrue(provider.is_connected())

if __name__ == '__main__':
    unittest.main()
