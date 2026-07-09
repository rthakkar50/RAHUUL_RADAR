import unittest
import json
import os
from core.performance_optimizer import PerformanceOptimizer, PerformanceMetrics, OptimizationStatus, OptimizationLevel

class TestPerformanceOptimizer(unittest.TestCase):
    def setUp(self):
        self.config_path = "tests/mock_performance_optimizer.json"
        config_data = {
            "performance_thresholds": {
                "maximum_cpu_percent": 70.0,
                "maximum_memory_mb": 500.0,
                "target_execution_time_ms": 200.0,
                "maximum_threads": 4,
                "cache_size_mb": 128.0
            },
            "optimization_settings": {
                "default_optimization_level": "STANDARD",
                "aggressive_cpu_threshold": 90.0,
                "aggressive_memory_threshold": 1000.0
            }
        }
        with open(self.config_path, "w") as f:
            json.dump(config_data, f)
            
        self.engine = PerformanceOptimizer(config_path=self.config_path)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_validation_rejects_negative_time(self):
        metrics = PerformanceMetrics(-10.0, 50.0, 200.0, 0.9, 2, 0, 0.0)
        result = self.engine.collect_metrics(metrics)
        self.assertEqual(result.status, OptimizationStatus.CRITICAL.value)
        self.assertIn("invalid metrics", result.warnings[0].lower())

    def test_validation_rejects_invalid_cpu(self):
        metrics = PerformanceMetrics(100.0, 150.0, 200.0, 0.9, 2, 0, 0.0)
        result = self.engine.collect_metrics(metrics)
        self.assertEqual(result.status, OptimizationStatus.CRITICAL.value)

    def test_validation_success(self):
        metrics = PerformanceMetrics(150.0, 50.0, 300.0, 0.9, 2, 0, 0.0)
        self.assertTrue(self.engine.validate_metrics(metrics))

    def test_analyze_cpu(self):
        score, msg = self.engine.analyze_cpu(50.0) # threshold 70
        self.assertIn("GOOD", msg)
        self.assertTrue(score < 100.0)
        
        score, msg = self.engine.analyze_cpu(80.0) # threshold 70, aggr 90
        self.assertIn("WARNING", msg)
        
        score, msg = self.engine.analyze_cpu(95.0) # aggr 90
        self.assertIn("CRITICAL", msg)
        self.assertEqual(score, 100.0)

    def test_analyze_memory(self):
        score, msg = self.engine.analyze_memory(400.0) # threshold 500
        self.assertIn("GOOD", msg)
        
        score, msg = self.engine.analyze_memory(600.0) # threshold 500, aggr 1000
        self.assertIn("WARNING", msg)
        
        score, msg = self.engine.analyze_memory(1200.0) # aggr 1000
        self.assertIn("CRITICAL", msg)

    def test_analyze_execution_time(self):
        score, msg = self.engine.analyze_execution_time(100.0) # target 200
        self.assertIn("GOOD", msg)
        
        score, msg = self.engine.analyze_execution_time(300.0) # target 200, severe 400
        self.assertIn("WARNING", msg)
        
        score, msg = self.engine.analyze_execution_time(500.0) # severe > 400
        self.assertIn("CRITICAL", msg)

    def test_analyze_cache(self):
        score, msg = self.engine.analyze_cache(0.9)
        self.assertIn("GOOD", msg)
        self.assertEqual(score, 10.0) # 100 - 90
        
        score, msg = self.engine.analyze_cache(0.4)
        self.assertIn("WARNING", msg)
        self.assertEqual(score, 60.0)
        
        score, msg = self.engine.analyze_cache(0.1)
        self.assertIn("CRITICAL", msg)
        self.assertEqual(score, 90.0)

    def test_collect_metrics_optimal(self):
        # Everything good: 100ms (50% target), 35% CPU (50% max), 250MB (50% max), 0.9 cache (10% penalty)
        # avg penalty = (50 + 50 + 50 + 10) / 4 = 160 / 4 = 40. Score = 60 (GOOD)
        metrics = PerformanceMetrics(100.0, 35.0, 250.0, 0.9, 2, 0, 0.0)
        result = self.engine.collect_metrics(metrics)
        # 100.0 - 40.0 = 60.0. > 40 is WARNING? Wait. 60 is GOOD, actually it needs > 70 for GOOD.
        # Let's use lower values to get > 70.
        # Exec 20ms (10% = 10 penalty)
        # CPU 7% (10% = 10 penalty)
        # Mem 50MB (10% = 10 penalty)
        # Cache 1.0 (0 penalty)
        # avg penalty = 30 / 4 = 7.5. Score = 92.5 (OPTIMAL)
        
        metrics = PerformanceMetrics(20.0, 7.0, 50.0, 1.0, 2, 0, 0.0)
        result = self.engine.collect_metrics(metrics)
        self.assertEqual(result.status, OptimizationStatus.OPTIMAL.value)
        self.assertEqual(result.optimization_level, OptimizationLevel.NONE.value)
        self.assertEqual(len(result.warnings), 0)

    def test_collect_metrics_critical(self):
        # Terrible stats
        metrics = PerformanceMetrics(500.0, 95.0, 1500.0, 0.1, 10, 100, 0.0)
        result = self.engine.collect_metrics(metrics)
        self.assertEqual(result.status, OptimizationStatus.CRITICAL.value)
        self.assertEqual(result.optimization_level, OptimizationLevel.AGGRESSIVE.value)
        self.assertTrue(len(result.warnings) > 0)
        self.assertTrue(len(result.recommendations) >= 3) # Cache, Thread, Flush

    def test_serialization(self):
        m = PerformanceMetrics(10.0, 10.0, 10.0, 0.5, 1, 0, 50.0)
        d = m.to_dict()
        self.assertEqual(d["cpu_usage"], 10.0)
        
        m2 = PerformanceMetrics.from_dict(d)
        self.assertEqual(m2.cpu_usage, 10.0)

if __name__ == '__main__':
    unittest.main()
