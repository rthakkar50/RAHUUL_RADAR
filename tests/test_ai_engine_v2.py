import unittest
from core.ai_v2.feature_engine import FeatureEngine
from core.ai_v2.feature_store import FeatureStore
from core.ai_v2.model_manager import ModelManager
from core.ai_v2.prediction_engine import PredictionEngine
from core.ai_v2.confidence_engine import ConfidenceEngine
from core.ai_v2.explainable_ai import ExplainableAI
from core.master_ai_engine import MasterAIEngine


class TestAIEngineV2(unittest.TestCase):

    def test_feature_engine(self):
        fe = FeatureEngine()
        context = {
            "close_price": 1000.0,
            "ema_200": 950.0,
            "rsi": 65.0,
            "volume_ratio": 2.1,
            "momentum_score": 80.0,
            "rs_score": 88.0
        }
        features = fe.extract_features_from_dict(context)
        self.assertIn("ema_200", features)
        self.assertEqual(features["ema_200"], 950.0)
        self.assertEqual(features["rsi_14"], 65.0)

    def test_feature_store(self):
        fs = FeatureStore.get_instance()
        features = {"rsi_14": 65.0, "volume_ratio": 1.5}
        fs.store_features("RELIANCE", features, "15m")
        retrieved = fs.get_features("RELIANCE", "15m")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["rsi_14"], 65.0)

    def test_model_manager_versioning_and_rollback(self):
        mm = ModelManager.get_instance()
        self.assertTrue(mm.switch_model("AI_v1"))
        self.assertEqual(mm.get_model_version(), "AI_v1")
        
        self.assertTrue(mm.switch_model("AI_v3"))
        self.assertEqual(mm.get_model_version(), "AI_v3")

        # Rollback to AI_v2
        self.assertTrue(mm.switch_model("AI_v2"))
        self.assertEqual(mm.get_model_version(), "AI_v2")

    def test_prediction_engine_latency_and_output(self):
        pe = PredictionEngine()
        fe = FeatureEngine()
        features = fe.extract_features_from_dict({"close_price": 1000.0, "rsi": 65.0, "volume_ratio": 1.8})
        
        res = pe.predict(features, mode="SWING")
        self.assertIn("predicted_signal", res)
        self.assertIn("probabilities", res)
        self.assertLess(res["inference_time_ms"], 100.0)

    def test_confidence_engine_bounding(self):
        ce = ConfidenceEngine()
        pred_res = {"predicted_signal": "BUY", "probabilities": {"BUY": 0.85, "SELL": 0.05, "HOLD": 0.10}}
        features = {"ema_20": 1000.0, "ema_200": 900.0, "volume_ratio": 1.8}
        context = {"market_regime": "Strong Bull Trend"}

        conf_res = ce.calculate_confidence(pred_res, features, context)
        confidence = conf_res["confidence"]
        self.assertTrue(0.0 <= confidence <= 100.0)

    def test_explainable_ai(self):
        xai = ExplainableAI()
        features = {"rsi_14": 65.0, "volume_ratio": 2.1, "ema_20": 1000.0, "ema_200": 900.0, "price_momentum": 5.2}
        res = xai.explain("BUY", 91.0, features, {})
        self.assertEqual(res["decision"], "BUY")
        self.assertTrue(len(res["reasons"]) > 0)

    def test_master_ai_engine_backward_compatibility(self):
        engine = MasterAIEngine()
        ctx = {
            "close_price": 500.0,
            "ema_200": 450.0,
            "trend_score": 85,
            "momentum_score": 80,
            "volume_score": 85,
            "rs_score": 88
        }
        res = engine.evaluate_signal("TATASTEEL", "BUY", ctx)
        self.assertIn("status", res)
        self.assertIn("score", res)
        self.assertIn("rating", res)
        self.assertIn("rejections", res)
        self.assertIn("report", res)


if __name__ == "__main__":
    unittest.main()
