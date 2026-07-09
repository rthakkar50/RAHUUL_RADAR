import unittest
import json
import os
from core.trade_execution_center import (
    TradeExecutionCenter, 
    ExecutionRequest, 
    ExecutionStatus, 
    ExecutionMode
)

class TestTradeExecutionCenter(unittest.TestCase):
    def setUp(self):
        self.config_path = "tests/mock_exec_rules.json"
        config_data = {
            "execution_settings": {
                "default_mode": "PAPER",
                "maximum_position_size": 1000,
                "maximum_concurrent_trades": 10,
                "execution_timeout_ms": 5000,
                "max_queue_size": 5
            },
            "risk_limits": {
                "maximum_risk_per_trade_pct": 2.0,
                "maximum_slippage_pct": 0.5,
                "minimum_confidence_to_execute": 75.0
            },
            "simulation_settings": {
                "default_slippage_pct": 0.1,
                "default_commission_pct": 0.05,
                "simulated_latency_ms": 50
            },
            "export_settings": {
                "default_export_path": "tests/mock_exec_exports/",
                "enable_pdf_export": True,
                "enable_csv_export": True
            }
        }
        with open(self.config_path, "w") as f:
            json.dump(config_data, f)
            
        self.engine = TradeExecutionCenter(config_path=self.config_path)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
            
        export_dir = "tests/mock_exec_exports/"
        if os.path.exists(export_dir):
            for file in os.listdir(export_dir):
                os.remove(os.path.join(export_dir, file))
            os.rmdir(export_dir)

    def get_valid_request(self):
        return ExecutionRequest(
            symbol="NIFTY", action="BUY", quantity=100,
            entry_price=100.0, stop_loss=99.0, # 1% risk
            target_1=102.0, target_2=105.0, target_3=110.0,
            confidence=90.0, position_size_factor=1.0,
            strategy_name="MockStrat", timestamp="2026-07-03T10:00:00"
        )

    def test_valid_paper_trade(self):
        req = self.get_valid_request()
        res = self.engine.execute_paper_trade(req)
        
        self.assertEqual(res.status, ExecutionStatus.EXECUTED.value)
        self.assertEqual(res.mode, ExecutionMode.PAPER.value)
        self.assertTrue(res.paper_trade_id.startswith("PT_"))
        self.assertTrue(res.risk_check)
        self.assertTrue(res.validation_check)

    def test_valid_simulation(self):
        req = self.get_valid_request()
        res = self.engine.execute_simulation(req)
        
        self.assertEqual(res.status, ExecutionStatus.EXECUTED.value)
        self.assertEqual(res.mode, ExecutionMode.SIMULATION.value)
        self.assertTrue(any("slippage" in w.lower() for w in res.warnings))

    def test_invalid_request_missing_symbol(self):
        req = self.get_valid_request()
        req.symbol = ""
        res = self.engine.execute_paper_trade(req)
        
        self.assertEqual(res.status, ExecutionStatus.REJECTED.value)
        self.assertIn("Validation Failed", res.message)

    def test_invalid_request_bad_prices(self):
        req = self.get_valid_request()
        req.entry_price = -10.0
        res = self.engine.execute_paper_trade(req)
        self.assertEqual(res.status, ExecutionStatus.REJECTED.value)

    def test_risk_rejection_max_size(self):
        req = self.get_valid_request()
        req.quantity = 5000 # Config max is 1000
        res = self.engine.execute_paper_trade(req)
        
        self.assertEqual(res.status, ExecutionStatus.REJECTED.value)
        self.assertIn("Position size exceeds maximum limit", res.message)

    def test_risk_rejection_max_risk_pct(self):
        req = self.get_valid_request()
        req.stop_loss = 90.0 # Risk is 10%, max is 2%
        res = self.engine.execute_paper_trade(req)
        
        self.assertEqual(res.status, ExecutionStatus.REJECTED.value)
        self.assertIn("exceeds limit", res.message)

    def test_validation_rejection_low_confidence(self):
        req = self.get_valid_request()
        req.confidence = 50.0 # Min is 75.0
        res = self.engine.execute_paper_trade(req)
        
        self.assertEqual(res.status, ExecutionStatus.REJECTED.value)
        self.assertIn("below threshold", res.message)

    def test_queue_overflow(self):
        req = self.get_valid_request()
        for _ in range(5):
            self.engine.queue_execution(req)
            
        with self.assertRaises(OverflowError):
            self.engine.queue_execution(req)

    def test_queue_cancellation(self):
        req = self.get_valid_request()
        exec_id = self.engine.queue_execution(req)
        
        self.assertTrue(self.engine.cancel_execution(exec_id))
        self.assertFalse(self.engine.cancel_execution(exec_id)) # Already cancelled

    def test_export(self):
        req = self.get_valid_request()
        res = self.engine.execute_paper_trade(req)
        
        json_path = self.engine.export_execution(res, "JSON")
        self.assertTrue(os.path.exists(json_path))
        
        csv_path = self.engine.export_execution(res, "CSV")
        self.assertTrue(os.path.exists(csv_path))

    def test_serialization(self):
        req = self.get_valid_request()
        d = req.to_dict()
        req2 = ExecutionRequest.from_dict(d)
        self.assertEqual(req2.symbol, "NIFTY")

if __name__ == '__main__':
    unittest.main()
