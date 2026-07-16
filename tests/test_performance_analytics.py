import unittest
from backtest.performance_analytics import PerformanceAnalytics

class TestPerformanceAnalytics(unittest.TestCase):
    def test_generate_summary_empty(self):
        analytics = PerformanceAnalytics()
        res = analytics.generate_summary([])
        self.assertEqual(res, {})

if __name__ == '__main__':
    unittest.main()
