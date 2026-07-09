import unittest
import json
import os
from core.institutional_validation_engine import (
    InstitutionalValidationEngine, 
    InstitutionalValidationInput, 
    InstitutionalValidationResult,
    ValidationStatus, 
    InstitutionGrade
)

class TestInstitutionalValidationEngine(unittest.TestCase):
    def setUp(self):
        self.config_path = "tests/mock_inst_val.json"
        config_data = {
            "validation_thresholds": {
                "minimum_overall_score": 75.0,
                "minimum_confidence": 70.0,
                "minimum_walk_forward_score": 60.0,
                "minimum_ranking_score": 65.0,
                "minimum_performance_score": 50.0,
                "maximum_drawdown_pct": 20.0
            },
            "grade_thresholds": {
                "A_PLUS": 95.0,
                "A": 85.0,
                "B": 75.0,
                "C": 65.0,
                "D": 50.0
            },
            "module_weights": {
                "false_signal_weight": 0.20,
                "mtf_weight": 0.10,
                "entry_weight": 0.15,
                "exit_weight": 0.10,
                "walk_forward_weight": 0.15,
                "ranking_weight": 0.10,
                "confidence_weight": 0.15,
                "performance_weight": 0.05
            },
            "export_settings": {
                "default_export_path": "tests/mock_val_exports/",
                "enable_pdf_export": True,
                "enable_csv_export": True
            }
        }
        with open(self.config_path, "w") as f:
            json.dump(config_data, f)
            
        self.engine = InstitutionalValidationEngine(config_path=self.config_path)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
            
        export_dir = "tests/mock_val_exports/"
        if os.path.exists(export_dir):
            for file in os.listdir(export_dir):
                os.remove(os.path.join(export_dir, file))
            os.rmdir(export_dir)

    def get_perfect_input(self):
        return InstitutionalValidationInput(
            false_signal_result={"status": "APPROVED"},
            mtf_result={"status": "CONFIRMED", "score": 100.0},
            entry_result={"entry_score": 100.0},
            exit_result={"exit_confidence": 100.0},
            walk_forward_result={"Validation Score": 100.0, "Metrics": {"Max Drawdown (%)": 5.0}},
            ranking_result={"Composite Score": 100.0},
            confidence_result={"confidence": 100.0, "status": "HIGH"},
            performance_result={"status": "OPTIMAL", "metrics": {"optimization_score": 100.0}}
        )

    def test_approved_validation(self):
        inputs = self.get_perfect_input()
        result = self.engine.build_validation_report(inputs)
        
        self.assertTrue(result.approved)
        self.assertEqual(result.validation_status, ValidationStatus.APPROVED.value)
        self.assertEqual(result.institution_grade, InstitutionGrade.A_PLUS.value)
        self.assertEqual(result.overall_score, 100.0)

    def test_rejected_critical_module_failure(self):
        inputs = self.get_perfect_input()
        # Trigger failure in False Signal
        inputs.false_signal_result = {"status": "REJECTED"}
        
        result = self.engine.build_validation_report(inputs)
        self.assertFalse(result.approved)
        self.assertEqual(result.validation_status, ValidationStatus.REJECTED.value)
        self.assertEqual(result.institution_grade, InstitutionGrade.FAILED.value)
        self.assertIn("FalseSignalDetector", result.failed_modules)

    def test_rejected_drawdown(self):
        inputs = self.get_perfect_input()
        # Exceed drawdown threshold of 20%
        inputs.walk_forward_result["Metrics"]["Max Drawdown (%)"] = 25.0
        
        result = self.engine.build_validation_report(inputs)
        self.assertFalse(result.approved)
        self.assertEqual(result.validation_status, ValidationStatus.REJECTED.value)
        self.assertIn("WalkForwardValidator (Drawdown)", result.failed_modules)

    def test_conditional_validation(self):
        inputs = self.get_perfect_input()
        # Lower scores so overall drops below 75 but above 65
        inputs.mtf_result["score"] = 0.0
        inputs.entry_result["entry_score"] = 0.0
        
        # We need overall to be between 65 and 75
        # Total weight of MTF (10%) and Entry (15%) is 25%.
        # Perfect is 100. Minus 25 is 75. 
        # Let's drop exit to 50 to bring score to 70.
        inputs.exit_result["exit_confidence"] = 50.0
        
        result = self.engine.build_validation_report(inputs)
        # Should be Conditional
        self.assertTrue(result.approved)
        self.assertEqual(result.validation_status, ValidationStatus.CONDITIONAL.value)

    def test_missing_modules(self):
        inputs = InstitutionalValidationInput() # Empty
        result = self.engine.build_validation_report(inputs)
        
        self.assertFalse(result.approved)
        self.assertEqual(result.validation_status, ValidationStatus.REJECTED.value)
        self.assertTrue(len(result.failed_modules) > 0)
        self.assertTrue(any("Missing input modules" in w for w in result.warnings))

    def test_export(self):
        inputs = self.get_perfect_input()
        result = self.engine.build_validation_report(inputs)
        
        json_path = self.engine.export_report(result, "JSON")
        self.assertTrue(os.path.exists(json_path))
        
        csv_path = self.engine.export_report(result, "CSV")
        self.assertTrue(os.path.exists(csv_path))

    def test_serialization(self):
        result = InstitutionalValidationResult(
            True, 80.0, "A", "APPROVED", [], [], [], 50.0
        )
        d = result.to_dict()
        r2 = InstitutionalValidationResult.from_dict(d)
        self.assertEqual(r2.institution_grade, "A")
        
if __name__ == '__main__':
    unittest.main()
