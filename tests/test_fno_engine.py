import time
import unittest
from core.fno_engine.symbol_manager import FNOSymbolManager
from core.fno_engine.expiry_engine import ExpiryEngine
from core.fno_engine.contract_selector import ContractSelector
from core.fno_engine.option_chain_engine import OptionChainEngine
from core.fno_engine.oi_engine import OIEngine
from core.fno_engine.pcr_engine import PCREngine
from core.fno_engine.maxpain_engine import MaxPainEngine
from core.fno_engine.greeks_engine import GreeksEngine
from core.fno_engine.iv_engine import IVEngine
from core.fno_engine.fno_ai_engine import FNOAIEngine
from core.fno_engine.fno_risk_engine import FNORiskEngine
from core.fno_engine.fno_signal_engine import FNOSignalEngine


class TestFNOEngine(unittest.TestCase):

    def setUp(self):
        self.symbol_manager = FNOSymbolManager()
        self.expiry_engine = ExpiryEngine()
        self.contract_selector = ContractSelector()
        self.option_chain_engine = OptionChainEngine.get_instance()
        self.greeks_engine = GreeksEngine()
        self.signal_engine = FNOSignalEngine()

    def test_symbol_manager_dynamic_universe(self):
        """Task 1 & 14: Dynamic symbol and lot size lookup."""
        nifty_info = self.symbol_manager.get_symbol_info("NIFTY")
        self.assertEqual(nifty_info["lot_size"], 25)
        self.assertEqual(nifty_info["step"], 50.0)

        banknifty_info = self.symbol_manager.get_symbol_info("BANKNIFTY")
        self.assertEqual(banknifty_info["lot_size"], 15)

        # Register custom crypto derivative
        self.symbol_manager.register_custom_symbol("SOLUSDT", lot_size=10, step=5.0, exchange="CRYPTO_DERIVATIVES")
        sol_info = self.symbol_manager.get_symbol_info("SOLUSDT")
        self.assertEqual(sol_info["exchange"], "CRYPTO_DERIVATIVES")

    def test_expiry_engine_calculations(self):
        """Task 2: Weekly and Monthly Expiry calculation."""
        current_w = self.expiry_engine.get_current_weekly_expiry("NIFTY")
        next_w = self.expiry_engine.get_next_weekly_expiry("NIFTY")
        monthly = self.expiry_engine.get_monthly_expiry("NIFTY")

        self.assertTrue(len(current_w) == 10)
        self.assertTrue(len(next_w) == 10)
        self.assertTrue(len(monthly) == 10)

    def test_contract_selector_strikes(self):
        """Task 3: ATM, ITM, OTM strike selection."""
        spot = 24230.0
        step = 50.0

        atm = self.contract_selector.select_strike(spot, option_type="CE", strike_type="ATM", step=step)
        self.assertEqual(atm, 24250.0)

        itm_ce = self.contract_selector.select_strike(spot, option_type="CE", strike_type="ITM", step=step)
        self.assertEqual(itm_ce, 24200.0)

        otm_ce = self.contract_selector.select_strike(spot, option_type="CE", strike_type="OTM", step=step)
        self.assertEqual(otm_ce, 24300.0)

    def test_option_chain_and_caching(self):
        """Task 4: Option chain structure and caching."""
        chain = self.option_chain_engine.get_option_chain("NIFTY", 24250.0, "2026-08-06")
        self.assertTrue(len(chain) > 0)
        item = chain[0]
        self.assertGreater(item.call_oi, 0)
        self.assertGreater(item.put_oi, 0)

    def test_greeks_engine_black_scholes(self):
        """Task 8: Black-Scholes Option Greeks calculation."""
        greeks_ce = self.greeks_engine.calculate_greeks(
            spot=24250.0, strike=24250.0, time_to_expiry_years=0.02, volatility=0.15, option_type="CE"
        )
        self.assertGreater(greeks_ce.delta, 0.40)
        self.assertGreater(greeks_ce.gamma, 0.0)
        self.assertLess(greeks_ce.theta, 0.0)

    def test_fno_signal_engine_end_to_end_and_performance(self):
        """Task 12 & 13: End-to-end signal output schema and <100ms latency requirement."""
        start_time = time.time()
        
        signal = self.signal_engine.generate_fno_signal(
            underlying="NIFTY",
            spot_price=24250.0,
            strike_type="ATM",
            expiry_type="CURRENT_WEEKLY",
            context_data={"vwap": 24240.0, "ema_20": 24230.0, "ema_200": 24000.0}
        )

        elapsed_ms = (time.time() - start_time) * 1000.0
        
        # Performance Assertion (<100ms)
        self.assertLess(elapsed_ms, 100.0, f"F&O Engine latency {elapsed_ms:.2f}ms exceeded 100ms requirement!")

        # Schema Verification (Task 12)
        required_keys = [
            "Symbol", "Underlying", "Expiry", "Strike", "OptionType",
            "Action", "Confidence", "Entry", "StopLoss", "Target1",
            "Target2", "Target3", "RiskReward", "Reasons"
        ]
        for key in required_keys:
            self.assertIn(key, signal, f"Missing key '{key}' in F&O Signal response!")

        self.assertEqual(signal["Underlying"], "NIFTY")
        self.assertIn(signal["Action"], ["BUY", "SELL", "WAIT"])
        self.assertTrue(0.0 <= signal["Confidence"] <= 100.0)


if __name__ == "__main__":
    unittest.main()
