import unittest
from ai_learning.dataset_builder import DatasetBuilder
from ai_learning.training_pipeline import OfflineTrainingPipeline
from ai_learning.model_registry import ModelRegistry
from ai_learning.champion_challenger import ChampionChallengerEngine
from ai_learning.promotion_manager import ModelPromotionManager
from ai_learning.drift_monitor import DriftMonitor
from ai_learning.hyperparameter_optimizer import HyperparameterOptimizer
from ai_learning.learning_reports import LearningReportEngine
from ai_learning.learning_scheduler import OfflineLearningScheduler


class TestAILearningPlatform(unittest.TestCase):

    def setUp(self):
        self.builder = DatasetBuilder()
        self.pipeline = OfflineTrainingPipeline()
        self.registry = ModelRegistry.get_instance()
        self.cmp_engine = ChampionChallengerEngine(self.registry)
        self.promotion_manager = ModelPromotionManager(self.cmp_engine, self.registry)
        self.drift_monitor = DriftMonitor()
        self.hp_optimizer = HyperparameterOptimizer()
        self.report_engine = LearningReportEngine()
        self.scheduler = OfflineLearningScheduler()

    def test_task_1_dataset_builder(self):
        """Task 1: Dataset Builder aggregates samples into FeatureDataset."""
        ds = self.builder.build_training_dataset()
        self.assertGreater(ds.sample_count, 0)
        self.assertTrue(ds.feature_count >= 17)

    def test_task_2_training_pipeline(self):
        """Task 2: Offline Training Pipeline produces artifact and evaluation report."""
        ds = self.builder.build_training_dataset()
        artifact, eval_rep = self.pipeline.train_candidate_model(ds, model_type="RANDOM_FOREST", version_label="AI_v3_test")
        self.assertEqual(artifact.version, "AI_v3_test")
        self.assertGreater(eval_rep.accuracy, 0.0)

    def test_task_3_model_registry(self):
        """Task 3: Model Registry stores version, checksum, and metadata."""
        champ = self.registry.get_champion()
        self.assertIn("version", champ)
        self.assertTrue(champ["is_champion"])

    def test_task_4_champion_challenger(self):
        """Task 4: Champion vs Challenger side-by-side metric comparison."""
        cmp_res = self.cmp_engine.compare_models("AI_v3_test", {"accuracy": 85.0, "profit_factor": 3.0, "max_drawdown": 2.5})
        self.assertIn("accuracy_diff", cmp_res.metric_diffs)
        self.assertEqual(cmp_res.recommended_winner, "AI_v3_test")

    def test_task_5_and_9_promotion_rules_and_safety_gate(self):
        """Task 5 & Task 9: Promotion Rules & Explicit Approval Safety Gate."""
        # Test rejection without explicit approval (Task 9)
        decision_no_app = self.promotion_manager.evaluate_promotion_eligibility(
            "AI_v3_test", {"accuracy": 85.0, "profit_factor": 3.0, "max_drawdown": 2.5}, explicit_approval=False
        )
        self.assertFalse(decision_no_app.is_approved)
        self.assertIn("Safety Violation: Explicit human/CTO approval required for model promotion.", decision_no_app.rejection_reasons)

        # Test approval with explicit approval & valid metrics
        decision_app = self.promotion_manager.evaluate_promotion_eligibility(
            "AI_v3_test", {"accuracy": 85.0, "profit_factor": 3.0, "max_drawdown": 2.5}, walk_forward_stability=0.85, explicit_approval=True
        )
        self.assertTrue(decision_app.is_approved)

    def test_task_6_drift_monitor(self):
        """Task 6: Feature & Prediction Drift (PSI) Monitoring."""
        drift_rep = self.drift_monitor.monitor_drift()
        self.assertGreaterEqual(drift_rep.feature_drift_score, 0.0)

    def test_task_7_and_8_optimizer_and_reports(self):
        """Task 7 & Task 8: Hyperparameter Optimizer & MLOps Learning Reports."""
        ds = self.builder.build_training_dataset()
        opt = self.hp_optimizer.optimize_hyperparameters(ds)
        self.assertEqual(opt["optimization_status"], "COMPLETED")

        artifact, eval_rep = self.pipeline.train_candidate_model(ds)
        rep = self.report_engine.generate_training_report(artifact, eval_rep)
        self.assertEqual(rep["model_id"], artifact.model_id)

    def test_offline_scheduler_cycle(self):
        """Offline learning cycle workflow test."""
        res = self.scheduler.run_offline_learning_cycle("AI_v4_candidate")
        self.assertEqual(res["status"], "COMPLETED_OFFLINE")


if __name__ == "__main__":
    unittest.main()
