import sys
import os
import unittest

# Ensure the root folder is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.adaptive_strategy_engine import (
    AdaptiveStrategyEngine,
    MarketEnvironment,
    StrategyType
)

class TestAdaptiveStrategyEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AdaptiveStrategyEngine()

    def test_initialization(self):
        """Test that the engine initializes without errors."""
        self.assertIsNotNone(self.engine)
        self.assertIsInstance(self.engine, AdaptiveStrategyEngine)

    def test_enums(self):
        """Test all enum values are present."""
        # MarketEnvironment enum values
        self.assertEqual(MarketEnvironment.UNKNOWN.name, "UNKNOWN")
        self.assertEqual(MarketEnvironment.BULL.name, "BULL")
        self.assertEqual(MarketEnvironment.STRONG_BULL.name, "STRONG_BULL")
        self.assertEqual(MarketEnvironment.BEAR.name, "BEAR")
        self.assertEqual(MarketEnvironment.STRONG_BEAR.name, "STRONG_BEAR")
        self.assertEqual(MarketEnvironment.SIDEWAYS.name, "SIDEWAYS")
        self.assertEqual(MarketEnvironment.VOLATILE.name, "VOLATILE")
        self.assertEqual(MarketEnvironment.LOW_VOLATILITY.name, "LOW_VOLATILITY")

        # StrategyType enum values
        self.assertEqual(StrategyType.SWING.name, "SWING")
        self.assertEqual(StrategyType.INTRADAY.name, "INTRADAY")
        self.assertEqual(StrategyType.SCALPING.name, "SCALPING")
        self.assertEqual(StrategyType.OPTION_SCALPING.name, "OPTION_SCALPING")
        self.assertEqual(StrategyType.NO_TRADE.name, "NO_TRADE")

    def test_strategy_names(self):
        """Test string representations of StrategyTypes."""
        self.assertEqual(self.engine.get_strategy_name(StrategyType.SWING), "Swing Trading")
        self.assertEqual(self.engine.get_strategy_name(StrategyType.INTRADAY), "Intraday Trading")
        self.assertEqual(self.engine.get_strategy_name(StrategyType.SCALPING), "Scalping")
        self.assertEqual(self.engine.get_strategy_name(StrategyType.OPTION_SCALPING), "Option Scalping")
        self.assertEqual(self.engine.get_strategy_name(StrategyType.NO_TRADE), "No Trade")

if __name__ == '__main__':
    unittest.main()
