import unittest
from backtest.simulated_broker import SimulatedBroker

class TestSimulatedBroker(unittest.TestCase):
    def test_initialization(self):
        broker = SimulatedBroker()
        self.assertIsNotNone(broker)

if __name__ == '__main__':
    unittest.main()
