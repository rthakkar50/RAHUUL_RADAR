"""
RAHUUL RADAR — AI Learning Platform: Offline Learning Scheduler
================================================================
Triggers offline dataset building, model retraining, and evaluation jobs.
"""

from typing import Dict, Any
from ai_learning.dataset_builder import DatasetBuilder
from ai_learning.training_pipeline import OfflineTrainingPipeline
from ai_learning.model_registry import ModelRegistry
from ai_learning.champion_challenger import ChampionChallengerEngine


class OfflineLearningScheduler:
    """
    Offline MLOps Job Scheduler.
    """

    def __init__(self):
        self.dataset_builder = DatasetBuilder()
        self.pipeline = OfflineTrainingPipeline()
        self.registry = ModelRegistry.get_instance()
        self.cmp_engine = ChampionChallengerEngine(self.registry)

    def run_offline_learning_cycle(self, version_label: str = "AI_v3_candidate") -> Dict[str, Any]:
        """Runs an offline dataset build, model training, and candidate evaluation cycle."""
        dataset = self.dataset_builder.build_training_dataset()
        artifact, eval_report = self.pipeline.train_candidate_model(
            dataset=dataset,
            model_type="RANDOM_FOREST",
            version_label=version_label
        )

        self.registry.register_model(artifact)
        comparison = self.cmp_engine.compare_models(version_label, artifact.metrics)

        return {
            "version": version_label,
            "sample_count": dataset.sample_count,
            "accuracy": eval_report.accuracy,
            "f1_score": eval_report.f1_score,
            "recommended_winner": comparison.recommended_winner,
            "status": "COMPLETED_OFFLINE"
        }
