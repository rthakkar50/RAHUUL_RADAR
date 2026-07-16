import unittest
from backtest.backtest_orchestrator import BacktestOrchestrator

class TestBacktestOrchestrator(unittest.TestCase):
    def test_initialization(self):
        orchestrator = BacktestOrchestrator()
        self.assertIsNotNone(orchestrator)

if __name__ == '__main__':
    unittest.main()
