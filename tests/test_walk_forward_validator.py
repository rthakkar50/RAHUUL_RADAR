import unittest
from datetime import datetime, timedelta
import json
import os
from core.walk_forward_validator import WalkForwardValidator, TradeResult, ValidationWindow, ValidationMetrics, ValidationStatus

class TestWalkForwardValidator(unittest.TestCase):
    def setUp(self):
        # Create a mock config
        self.config_path = "tests/mock_walk_forward.json"
        config_data = {
            "validation_thresholds": {
                "minimum_win_rate": 45.0,
                "minimum_profit_factor": 1.5,
                "maximum_drawdown": 20.0,
                "minimum_trades": 5,
                "minimum_expectancy": 0.2,
                "minimum_sharpe_ratio": 1.0
            },
            "window_settings": {
                "window_size_days": 100,
                "training_split_percentage": 70,
                "testing_split_percentage": 30
            }
        }
        with open(self.config_path, "w") as f:
            json.dump(config_data, f)
            
        self.validator = WalkForwardValidator(config_path=self.config_path)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_window_creation(self):
        start = datetime(2023, 1, 1)
        end = datetime(2023, 12, 31)
        windows = self.validator.create_validation_windows(start, end)
        
        self.assertTrue(len(windows) > 0)
        w1 = windows[0]
        self.assertEqual(w1.training_start, start)
        self.assertEqual(w1.training_end, start + timedelta(days=70))
        self.assertEqual(w1.testing_start, start + timedelta(days=70))
        self.assertEqual(w1.testing_end, start + timedelta(days=100))

    def _create_mock_trades(self, pnl_list):
        trades = []
        base_time = datetime(2023, 1, 1)
        for i, pnl in enumerate(pnl_list):
            trades.append(TradeResult(
                entry_time=base_time + timedelta(days=i),
                exit_time=base_time + timedelta(days=i, hours=1),
                symbol="NIFTY",
                direction="BUY" if pnl > 0 else "SELL",
                entry_price=100.0,
                exit_price=100.0 + pnl,
                quantity=1,
                profit_loss=pnl,
                risk_reward=2.0,
                status="CLOSED"
            ))
        return trades

    def test_metrics_calculation(self):
        # 3 wins, 2 losses
        pnl_list = [10.0, 15.0, -5.0, 20.0, -10.0]
        trades = self._create_mock_trades(pnl_list)
        
        metrics = self.validator.calculate_metrics("TestStrategy", trades)
        self.assertEqual(metrics.total_trades, 5)
        self.assertEqual(metrics.winning_trades, 3)
        self.assertEqual(metrics.losing_trades, 2)
        self.assertEqual(metrics.win_rate, 60.0) # 3/5
        self.assertEqual(metrics.gross_profit, 45.0)
        self.assertEqual(metrics.gross_loss, -15.0)
        self.assertEqual(metrics.net_profit, 30.0)
        self.assertEqual(metrics.profit_factor, 3.0) # 45 / 15
        
        # Max drawdown: Peak after trade 2 is 25. Then -5 -> 20 (DD = 5/25 = 20%). Then +20 -> 40. Then -10 -> 30 (DD = 10/40 = 25%).
        # So max DD should be 25%
        self.assertEqual(metrics.maximum_drawdown, 25.0)

    def test_validation_pass(self):
        # High win rate, high PF, low drawdown
        pnl_list = [10.0, 10.0, 10.0, -2.0, 10.0, 10.0]
        trades = self._create_mock_trades(pnl_list)
        metrics = self.validator.calculate_metrics("PassStrat", trades)
        status = self.validator.validate_strategy(metrics)
        self.assertEqual(status, ValidationStatus.PASSED)

    def test_validation_fail_trades(self):
        # Not enough trades
        pnl_list = [10.0, 10.0]
        trades = self._create_mock_trades(pnl_list)
        metrics = self.validator.calculate_metrics("FailStrat", trades)
        status = self.validator.validate_strategy(metrics)
        self.assertEqual(status, ValidationStatus.FAILED)

    def test_validation_fail_drawdown(self):
        # Good trades but a massive drawdown > 20%
        pnl_list = [100.0, -50.0, 10.0, 10.0, 10.0, 10.0] 
        # peak 100 -> DD 50%
        trades = self._create_mock_trades(pnl_list)
        metrics = self.validator.calculate_metrics("FailDD", trades)
        status = self.validator.validate_strategy(metrics)
        self.assertEqual(status, ValidationStatus.FAILED)

    def test_validation_warning(self):
        # Win rate slightly below 45% (say 40%), PF > 1.5, DD < 20%
        # We need 2 wins, 3 losses -> 40% win rate
        # 2 wins = 20.0, 3 losses = -3.0 (PF = 20/3 = 6.6)
        pnl_list = [10.0, -1.0, -1.0, 10.0, -1.0]
        trades = self._create_mock_trades(pnl_list)
        metrics = self.validator.calculate_metrics("WarnStrat", trades)
        status = self.validator.validate_strategy(metrics)
        # Assuming win rate warning triggers if >= 0.9 * threshold (40.5%). 40% is < 40.5%, so it would fail!
        # Let's adjust to 42% win rate. Need more trades.
        # 3 wins, 4 losses -> 3/7 = 42.8%
        # Threshold 45%. 0.9 * 45 = 40.5%. 42.8% is warning.
        pnl_list = [10.0, -1.0, -1.0, 10.0, -1.0, 10.0, -1.0]
        trades = self._create_mock_trades(pnl_list)
        metrics = self.validator.calculate_metrics("WarnStrat", trades)
        status = self.validator.validate_strategy(metrics)
        self.assertEqual(status, ValidationStatus.WARNING)

    def test_serialization(self):
        tr = TradeResult(datetime.now(), datetime.now(), "NIFTY", "BUY", 100, 110, 1, 10, 2, "CLOSED")
        tr_dict = tr.to_dict()
        self.assertEqual(tr_dict["profit_loss"], 10)
        
        tr_restored = TradeResult.from_dict(tr_dict)
        self.assertEqual(tr_restored.profit_loss, 10)

    def test_empty_trades(self):
        metrics = self.validator.calculate_metrics("Empty", [])
        self.assertEqual(metrics.status, ValidationStatus.FAILED)
        self.assertEqual(metrics.total_trades, 0)
        
        status = self.validator.validate_strategy(metrics)
        self.assertEqual(status, ValidationStatus.FAILED)

if __name__ == '__main__':
    unittest.main()
