"""
RAHUUL RADAR — Enterprise AI Learning Platform Package
======================================================
Offline MLOps, Model Registry, Champion-Challenger, and Drift Monitoring Platform.
"""

from ai_learning.ai_learning_models import (
    DatasetMetadata, ModelArtifact, EvaluationReport,
    ChampionChallengerComparison, DriftReport, PromotionDecision
)
from ai_learning.feature_dataset import FeatureDataset
from ai_learning.dataset_builder import DatasetBuilder
from ai_learning.model_evaluator import ModelEvaluator
from ai_learning.training_pipeline import OfflineTrainingPipeline
from ai_learning.model_registry import ModelRegistry
from ai_learning.champion_challenger import ChampionChallengerEngine
from ai_learning.promotion_manager import ModelPromotionManager
from ai_learning.drift_monitor import DriftMonitor
from ai_learning.hyperparameter_optimizer import HyperparameterOptimizer
from ai_learning.learning_reports import LearningReportEngine
from ai_learning.learning_scheduler import OfflineLearningScheduler

__all__ = [
    "DatasetMetadata", "ModelArtifact", "EvaluationReport",
    "ChampionChallengerComparison", "DriftReport", "PromotionDecision",
    "FeatureDataset", "DatasetBuilder", "ModelEvaluator",
    "OfflineTrainingPipeline", "ModelRegistry", "ChampionChallengerEngine",
    "ModelPromotionManager", "DriftMonitor", "HyperparameterOptimizer",
    "LearningReportEngine", "OfflineLearningScheduler"
]
