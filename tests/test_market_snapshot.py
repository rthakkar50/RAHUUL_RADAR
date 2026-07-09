import sys
import os
import unittest

# Ensure the root folder is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.adaptive_strategy_engine import (
    AdaptiveStrategyEngine,
    MarketSnapshot,
    MarketEnvironment,
    StrategyType
)

class TestMarketSnapshotEvaluator(unittest.TestCase):
    def setUp(self):
        self.engine = AdaptiveStrategyEngine()

    def test_market_snapshot_creation(self):
        """Tests that a MarketSnapshot object is instantiated correctly with all fields."""
        snapshot = MarketSnapshot(
            trend_direction="BULL",
            adx=35.0,
            atr=1.5,
            rsi=62.0,
            price_above_vwap=True,
            volume_ratio=1.8,
            market_breadth=72.0,
            sector_strength=80.0,
            relative_strength=90.0,
            option_chain_bias="BULLISH"
        )
        self.assertEqual(snapshot.trend_direction, "BULL")
        self.assertEqual(snapshot.adx, 35.0)
        self.assertEqual(snapshot.atr, 1.5)
        self.assertTrue(snapshot.price_above_vwap)
        self.assertEqual(snapshot.option_chain_bias, "BULLISH")

    def test_evaluate_snapshot_strong_bull(self):
        """Tests evaluate_snapshot with data triggering STRONG_BULL -> INTRADAY."""
        snapshot = MarketSnapshot(
            trend_direction="BULL",
            adx=32.0,
            atr=1.2,
            rsi=60.0,
            price_above_vwap=True,
            volume_ratio=1.5,
            market_breadth=70.0,
            sector_strength=75.0,
            relative_strength=80.0,
            option_chain_bias="BULLISH"
        )
        env, strat, strat_name = self.engine.evaluate_snapshot(snapshot)
        self.assertEqual(env, MarketEnvironment.STRONG_BULL)
        self.assertEqual(strat, StrategyType.INTRADAY)
        self.assertEqual(strat_name, "Intraday Trading")

    def test_evaluate_snapshot_low_volatility(self):
        """Tests evaluate_snapshot with data triggering LOW_VOLATILITY -> NO_TRADE."""
        snapshot = MarketSnapshot(
            trend_direction="BULL",
            adx=22.0,
            atr=0.1,  # extremely low
            rsi=50.0,
            price_above_vwap=False,
            volume_ratio=0.8,
            market_breadth=50.0,
            sector_strength=50.0,
            relative_strength=50.0,
            option_chain_bias="NEUTRAL"
        )
        env, strat, strat_name = self.engine.evaluate_snapshot(snapshot)
        self.assertEqual(env, MarketEnvironment.LOW_VOLATILITY)
        self.assertEqual(strat, StrategyType.NO_TRADE)
        self.assertEqual(strat_name, "No Trade")

if __name__ == '__main__':
    unittest.main()
