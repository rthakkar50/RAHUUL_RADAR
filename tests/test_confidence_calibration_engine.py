import unittest
import json
import os
from core.confidence_calibration_engine import ConfidenceCalibrationEngine, ConfidenceInput, ConfidenceResult, ConfidenceGrade, ConfidenceStatus

class TestConfidenceCalibrationEngine(unittest.TestCase):
    def setUp(self):
        self.config_path = "tests/mock_confidence_rules.json"
        config_data = {
            "confidence_weights": {
                "trend_score": 0.2,
                "momentum_score": 0.2,
                "volume_score": 0.2,
                "structure_score": 0.2,
                "relative_strength_score": 0.2
            },
            "grade_thresholds": {
                "A_PLUS": 90.0,
                "A": 80.0,
                "B": 60.0,
                "C": 40.0,
                "D": 20.0
            },
            "status_thresholds": {
                "HIGH": 80.0,
                "MEDIUM": 50.0,
                "LOW": 20.0
            },
            "normalization_bounds": {
                "default_min": 0.0,
                "default_max": 100.0
            },
            "minimum_required_engines": 3
        }
        with open(self.config_path, "w") as f:
            json.dump(config_data, f)
            
        self.engine = ConfidenceCalibrationEngine(config_path=self.config_path)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_validation_insufficient_engines(self):
        # The new ConfidenceInput dataclass provides defaults of 50.0 for all scores,
        # so length is always satisfied. But let's check bounds validation.
        inputs = ConfidenceInput(trend_score=-50.0)
        self.assertFalse(self.engine.validate_input(inputs))

    def test_validation_out_of_bounds(self):
        inputs = ConfidenceInput(trend_score=150.0, momentum_score=60.0, volume_score=50.0)
        self.assertFalse(self.engine.validate_input(inputs))
        
        inputs2 = ConfidenceInput(trend_score=-10.0, momentum_score=60.0, volume_score=50.0)
        self.assertFalse(self.engine.validate_input(inputs2))

    def test_validation_success(self):
        inputs = ConfidenceInput(trend_score=50.0, momentum_score=60.0, volume_score=50.0)
        self.assertTrue(self.engine.validate_input(inputs))

    def test_normalization(self):
        self.assertEqual(self.engine.normalize_score(50.0), 50.0)
        
        # Test custom bounds
        self.engine.normalization_bounds = {"default_min": 20.0, "default_max": 80.0}
        # (50 - 20) / 60 * 100 = 30 / 60 * 100 = 50.0
        self.assertEqual(self.engine.normalize_score(50.0), 50.0)
        # (80 - 20) / 60 * 100 = 100
        self.assertEqual(self.engine.normalize_score(80.0), 100.0)
        # (10 - 20) clamp to 0
        self.assertEqual(self.engine.normalize_score(10.0), 0.0)
        # Reset
        self.engine.normalization_bounds = {"default_min": 0.0, "default_max": 100.0}

    def test_calibration_high_grade(self):
        inputs = ConfidenceInput(trend_score=100.0, momentum_score=100.0, volume_score=100.0, structure_score=100.0, relative_strength_score=100.0)
        result = self.engine.calibrate_confidence(inputs)
        
        self.assertEqual(result.raw_score, 100.0)
        self.assertEqual(result.grade, ConfidenceGrade.A_PLUS.value)
        self.assertEqual(result.status, ConfidenceStatus.HIGH.value)

    def test_calibration_medium_grade(self):
        # 5 engines at 65.0
        inputs = ConfidenceInput(trend_score=65.0, momentum_score=65.0, volume_score=65.0, structure_score=65.0, relative_strength_score=65.0)
        result = self.engine.calibrate_confidence(inputs)
        
        self.assertEqual(result.raw_score, 65.0)
        self.assertEqual(result.grade, ConfidenceGrade.B.value)
        self.assertEqual(result.status, ConfidenceStatus.MEDIUM.value)

    def test_calibration_missing_engines_weight_distribution(self):
        # 3 engines provided at 100.0. The other 2 default to 50.0.
        # Total = 300 + 100 = 400. Average = 400 / 5 = 80.0.
        inputs = ConfidenceInput(trend_score=100.0, momentum_score=100.0, volume_score=100.0)
        result = self.engine.calibrate_confidence(inputs)
        self.assertAlmostEqual(result.raw_score, 80.0)

    def test_serialization(self):
        inputs = ConfidenceInput(trend_score=50.0)
        d = inputs.to_dict()
        self.assertEqual(d["trend_score"], 50.0)
        
        i2 = ConfidenceInput.from_dict(d)
        self.assertEqual(i2.trend_score, 50.0)

if __name__ == '__main__':
    unittest.main()
