import unittest
import json
import os
from core.strategy_ranking_engine import StrategyRankingEngine, StrategyMetrics, StrategyRank, RankingStatus

class TestStrategyRankingEngine(unittest.TestCase):
    def setUp(self):
        self.config_path = "tests/mock_strategy_ranking.json"
        config_data = {
            "ranking_weights": {
                "win_rate_weight": 0.3,
                "profit_factor_weight": 0.3,
                "drawdown_weight": 0.2,
                "expectancy_weight": 0.1,
                "risk_reward_weight": 0.05,
                "trade_count_weight": 0.05
            },
            "ranking_thresholds": {
                "minimum_validation_score": 30.0
            },
            "status_thresholds": {
                "excellent_score": 80.0,
                "good_score": 60.0,
                "average_score": 40.0,
                "poor_score": 30.0
            }
        }
        with open(self.config_path, "w") as f:
            json.dump(config_data, f)
            
        self.engine = StrategyRankingEngine(config_path=self.config_path)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_validate_metrics(self):
        valid = StrategyMetrics("S1", 50.0, 2.0, 0.5, 2.0, 10.0, 1000.0, 50, 10.0, "PASSED")
        self.assertTrue(self.engine.validate_metrics(valid))
        
        invalid_wr = StrategyMetrics("S2", 101.0, 2.0, 0.5, 2.0, 10.0, 1000.0, 50, 10.0, "PASSED")
        self.assertFalse(self.engine.validate_metrics(invalid_wr))
        
        invalid_dd = StrategyMetrics("S3", 50.0, 2.0, 0.5, 2.0, -5.0, 1000.0, 50, 10.0, "PASSED")
        self.assertFalse(self.engine.validate_metrics(invalid_dd))

    def test_calculate_overall_score(self):
        m = StrategyMetrics("S1", 100.0, 5.0, 1.0, 5.0, 0.0, 1000.0, 1000, 10.0, "PASSED")
        # Should be a perfect 100 score based on bounds
        score = self.engine.calculate_overall_score(m)
        self.assertAlmostEqual(score, 100.0)
        
        m2 = StrategyMetrics("S2", 0.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0, 10.0, "PASSED")
        score2 = self.engine.calculate_overall_score(m2)
        self.assertAlmostEqual(score2, 0.0)

    def test_ranking_sorting(self):
        s1 = StrategyMetrics("S1", 60.0, 1.5, 0.2, 1.5, 20.0, 500.0, 100, 10.0, "PASSED")
        s2 = StrategyMetrics("S2", 80.0, 2.5, 0.5, 2.0, 10.0, 1000.0, 200, 10.0, "PASSED")
        s3 = StrategyMetrics("S3", 40.0, 0.8, -0.1, 0.8, 30.0, -100.0, 50, 10.0, "WARNING")
        
        ranked = self.engine.rank_strategies([s1, s2, s3])
        self.assertEqual(len(ranked), 3)
        self.assertEqual(ranked[0].strategy_name, "S2")
        self.assertEqual(ranked[1].strategy_name, "S1")
        self.assertEqual(ranked[2].strategy_name, "S3")

    def test_tie_breaking(self):
        # Same exact metrics except net profit
        s1 = StrategyMetrics("S1", 50.0, 2.0, 0.5, 2.0, 10.0, 1000.0, 50, 10.0, "PASSED")
        s2 = StrategyMetrics("S2", 50.0, 2.0, 0.5, 2.0, 10.0, 2000.0, 50, 10.0, "PASSED")
        
        ranked = self.engine.rank_strategies([s1, s2])
        self.assertEqual(ranked[0].strategy_name, "S2")

    def test_rejection_and_top_n(self):
        s1 = StrategyMetrics("S1", 10.0, 0.5, 0.0, 0.5, 80.0, -500.0, 10, 10.0, "FAILED")
        s2 = StrategyMetrics("S2", 90.0, 3.0, 0.8, 2.5, 5.0, 2000.0, 300, 10.0, "PASSED")
        
        ranked = self.engine.rank_strategies([s1, s2])
        # S1 should be REJECTED because it explicitly says FAILED validation status
        self.assertEqual(ranked[1].confidence, RankingStatus.REJECTED.value)
        
        top1 = self.engine.get_top_n(ranked, 1)
        self.assertEqual(len(top1), 1)
        self.assertEqual(top1[0].strategy_name, "S2")
        
        best = self.engine.get_best_strategy(ranked)
        self.assertEqual(best.strategy_name, "S2")

    def test_serialization(self):
        r = StrategyRank(1, "S1", 95.0, "EXCELLENT", "Good")
        d = r.to_dict()
        self.assertEqual(d["rank"], 1)

if __name__ == '__main__':
    unittest.main()
