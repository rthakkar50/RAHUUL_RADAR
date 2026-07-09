import unittest
import json
import os
from core.master_ai_decision_engine import (
    MasterAIDecisionEngine, 
    DecisionInput, 
    DecisionAction, 
    DecisionStatus, 
    DecisionGrade
)

class TestMasterAIDecisionEngine(unittest.TestCase):
    def setUp(self):
        self.config_path = "tests/mock_master_ai.json"
        config_data = {
            "validation_thresholds": {
                "minimum_confidence": 75.0,
                "minimum_institutional_grade": "B",
                "minimum_walk_forward_score": 60.0,
                "minimum_strategy_rank": 65.0,
                "maximum_risk_level": 5.0
            },
            "decision_thresholds": {
                "buy_threshold": 80.0,
                "strong_buy_threshold": 90.0,
                "sell_threshold": 20.0,
                "strong_sell_threshold": 10.0
            },
            "position_size_multipliers": {
                "A_PLUS": 1.00,
                "A": 0.75,
                "B": 0.50,
                "C": 0.25,
                "D": 0.10,
                "FAILED": 0.00
            },
            "export_settings": {
                "default_export_path": "tests/mock_ai_exports/",
                "enable_pdf_export": True,
                "enable_csv_export": True
            }
        }
        with open(self.config_path, "w") as f:
            json.dump(config_data, f)
            
        self.engine = MasterAIDecisionEngine(config_path=self.config_path)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
            
        export_dir = "tests/mock_ai_exports/"
        if os.path.exists(export_dir):
            for file in os.listdir(export_dir):
                os.remove(os.path.join(export_dir, file))
            os.rmdir(export_dir)

    def get_perfect_input(self):
        return DecisionInput(
            symbol="NIFTY",
            timestamp="2026-07-03T10:00:00",
            market_regime="BULLISH",
            false_signal_result={"status": "APPROVED"},
            mtf_result={"score": 100.0},
            entry_result={
                "entry_score": 100.0, 
                "recommended_entry": 100.0, 
                "stop_loss": 98.0, 
                "target_1": 104.0, 
                "target_2": 108.0, 
                "target_3": 112.0
            },
            exit_result={"exit_action": "HOLD", "trailing_stop": 95.0},
            walk_forward_result={"Validation Score": 100.0},
            ranking_result={"Composite Score": 100.0},
            confidence_result={"confidence": 95.0},
            performance_result={"status": "OPTIMAL"},
            institutional_result={"institution_grade": "A_PLUS", "validation_status": "APPROVED"}
        )

    def test_strong_buy(self):
        inputs = self.get_perfect_input()
        result = self.engine.build_decision_report(inputs)
        
        self.assertEqual(result.action, DecisionAction.BUY.value)
        self.assertEqual(result.decision_status, DecisionStatus.EXECUTE.value)
        self.assertEqual(result.position_size_factor, 1.0)
        self.assertEqual(result.overall_score, 100.0)
        self.assertEqual(result.risk_level, 2.0) # (100-98)/100 = 2%

    def test_sell_due_to_exit_action(self):
        inputs = self.get_perfect_input()
        inputs.exit_result["exit_action"] = "EXIT"
        
        result = self.engine.build_decision_report(inputs)
        self.assertEqual(result.action, DecisionAction.SELL.value)

    def test_wait_due_to_neutral_score(self):
        inputs = self.get_perfect_input()
        inputs.mtf_result["score"] = 50.0
        inputs.entry_result["entry_score"] = 50.0
        inputs.walk_forward_result["Validation Score"] = 50.0
        inputs.ranking_result["Composite Score"] = 50.0
        # Overall score will be 50.0, action WAIT
        
        result = self.engine.build_decision_report(inputs)
        self.assertEqual(result.action, DecisionAction.WAIT.value)
        self.assertEqual(result.decision_status, DecisionStatus.EXECUTE.value) # Execution of WAIT is valid

    def test_rejected_due_to_false_signal(self):
        inputs = self.get_perfect_input()
        inputs.false_signal_result["status"] = "REJECTED"
        
        result = self.engine.build_decision_report(inputs)
        self.assertEqual(result.action, DecisionAction.REJECT.value)
        self.assertEqual(result.decision_status, DecisionStatus.BLOCKED.value)
        self.assertEqual(result.position_size_factor, 0.0)

    def test_rejected_due_to_institutional_grade(self):
        inputs = self.get_perfect_input()
        inputs.institutional_result["institution_grade"] = "FAILED"
        inputs.institutional_result["validation_status"] = "REJECTED"
        
        result = self.engine.build_decision_report(inputs)
        self.assertEqual(result.action, DecisionAction.REJECT.value)
        self.assertEqual(result.decision_status, DecisionStatus.BLOCKED.value)
        self.assertEqual(result.position_size_factor, 0.0)

    def test_wait_due_to_high_risk(self):
        inputs = self.get_perfect_input()
        inputs.entry_result["stop_loss"] = 90.0 # Risk = 10% (exceeds max 5%)
        
        result = self.engine.build_decision_report(inputs)
        self.assertEqual(result.action, DecisionAction.BUY.value)
        # Even though it's a BUY, risk makes it WAIT
        self.assertEqual(result.decision_status, DecisionStatus.WAIT.value)
        self.assertTrue(any("Risk level" in w for w in result.warnings))

    def test_wait_due_to_low_confidence(self):
        inputs = self.get_perfect_input()
        inputs.confidence_result["confidence"] = 50.0 # Below min 75
        
        result = self.engine.build_decision_report(inputs)
        self.assertEqual(result.decision_status, DecisionStatus.WAIT.value)
        self.assertTrue(any("Confidence" in w for w in result.warnings))

    def test_missing_modules(self):
        inputs = DecisionInput(symbol="TEST", timestamp="now", market_regime="BULL")
        result = self.engine.build_decision_report(inputs)
        
        self.assertEqual(result.action, DecisionAction.REJECT.value)
        self.assertEqual(result.decision_status, DecisionStatus.BLOCKED.value)
        self.assertTrue(any("Missing modules" in w for w in result.warnings))

    def test_export(self):
        inputs = self.get_perfect_input()
        result = self.engine.build_decision_report(inputs)
        
        json_path = self.engine.export_decision(result, "JSON")
        self.assertTrue(os.path.exists(json_path))
        
        csv_path = self.engine.export_decision(result, "CSV")
        self.assertTrue(os.path.exists(csv_path))

    def test_serialization(self):
        i = DecisionInput(symbol="T", timestamp="T", market_regime="M")
        d = i.to_dict()
        i2 = DecisionInput.from_dict(d)
        self.assertEqual(i2.symbol, "T")

if __name__ == '__main__':
    unittest.main()
