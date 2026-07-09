import sys
import os
import unittest

# Ensure the root folder is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.master_signal_pipeline import MasterSignalPipeline

class DummyEngine:
    def __init__(self, return_value):
        self.return_value = return_value

    def calculate(self, *args, **kwargs):
        return self.return_value

    def evaluate(self, *args, **kwargs):
        return self.return_value

class FaultyEngine:
    def calculate(self, *args, **kwargs):
        raise ValueError("Simulated engine failure")

class TestMasterSignalPipeline(unittest.TestCase):
    def test_pipeline_initialization(self):
        """Tests that pipeline initializes with standard empty settings."""
        pipeline = MasterSignalPipeline()
        self.assertEqual(pipeline.engines, {})

    def test_collect_results_success(self):
        """Tests that collect_results successfully calls engines and aggregates results."""
        engines = {
            "trend": DummyEngine("BULL"),
            "momentum": DummyEngine("OVERSOLD"),
            "volume": DummyEngine("HIGH"),
            "structure": DummyEngine("SUPPORT"),
            "risk": DummyEngine("LOW_RISK"),
            "relative_strength": DummyEngine("STRONG"),
            "sector_rotation": DummyEngine("LEADING"),
            "adaptive_strategy": DummyEngine("SWING"),
            "master_ai": DummyEngine("BUY")
        }
        pipeline = MasterSignalPipeline(engines=engines)
        results = pipeline.collect_results(symbol="RELIANCE")
        
        import inspect; print("COLLECT RESULTS FUNC:", repr(pipeline.collect_results), "MODULE:", getattr(pipeline.collect_results, "__module__", None), "CLOSURE:", inspect.getclosurevars(pipeline.collect_results) if hasattr(pipeline.collect_results, "__code__") else "NO_CODE"); self.assertEqual(results["trend"], "BULL")
        self.assertEqual(results["momentum"], "OVERSOLD")
        self.assertEqual(results["risk"], "LOW_RISK")
        self.assertEqual(results["master_ai"], "BUY")

    def test_collect_results_faulty_engine(self):
        """Tests that collect_results handles individual engine crashes gracefully."""
        engines = {
            "trend": DummyEngine("BULL"),
            "momentum": FaultyEngine(),  # will raise exception
            "volume": DummyEngine("HIGH")
        }
        pipeline = MasterSignalPipeline(engines=engines)
        results = pipeline.collect_results(symbol="RELIANCE")
        
        import inspect; print("COLLECT RESULTS FUNC:", repr(pipeline.collect_results), "MODULE:", getattr(pipeline.collect_results, "__module__", None), "CLOSURE:", inspect.getclosurevars(pipeline.collect_results) if hasattr(pipeline.collect_results, "__code__") else "NO_CODE"); self.assertEqual(results["trend"], "BULL")
        self.assertIsNone(results["momentum"])  # Error caught, marked None
        self.assertEqual(results["volume"], "HIGH")

    def test_validate(self):
        """Tests that validate flags incomplete or complete engine outputs."""
        pipeline = MasterSignalPipeline()
        
        # Incomplete results
        incomplete = {
            "trend": "BULL",
            "momentum": "OVERSOLD"
        }
        valid, missing = pipeline.validate(incomplete)
        self.assertFalse(valid)
        self.assertIn("volume", missing)
        self.assertIn("master_ai", missing)

        # Complete results
        complete = {
            "trend": "BULL",
            "momentum": "OVERSOLD",
            "volume": "HIGH",
            "structure": "SUPPORT",
            "risk": "LOW_RISK",
            "relative_strength": "STRONG",
            "sector_rotation": "LEADING",
            "adaptive_strategy": "SWING",
            "master_ai": "BUY"
        }
        valid, missing = pipeline.validate(complete)
        self.assertTrue(valid)
        self.assertEqual(len(missing), 0)

    def test_generate_summary(self):
        """Tests that generate_summary formats outputs correctly."""
        pipeline = MasterSignalPipeline()
        collected = {
            "trend": "BULL",
            "momentum": "OVERSOLD",
            "volume": "HIGH",
            "structure": "SUPPORT",
            "risk": "LOW_RISK",
            "relative_strength": "STRONG",
            "sector_rotation": "LEADING",
            "adaptive_strategy": "SWING",
            "master_ai": "BUY"
        }
        summary = pipeline.generate_summary(collected, "SUCCESS")
        
        self.assertEqual(summary["Market Trend"], "BULL")
        self.assertEqual(summary["Momentum"], "OVERSOLD")
        self.assertEqual(summary["Pipeline Status"], "SUCCESS")

if __name__ == '__main__':
    unittest.main()
