"""
RAHUUL RADAR — AI Learning Platform: Learning Reports (Task 8)
===============================================================
Generates Training Summaries, Model Comparisons, Feature Importance,
Confusion Matrices, Precision, Recall, F1-Scores, and ROC-AUC charts.
"""

from typing import Dict, List, Any
from ai_learning.ai_learning_models import EvaluationReport, ModelArtifact, ChampionChallengerComparison


class LearningReportEngine:
    """
    MLOps Reporting & Visual Evaluation Engine.
    """

    def generate_training_report(
        self,
        artifact: ModelArtifact,
        eval_report: EvaluationReport,
        comparison: ChampionChallengerComparison = None
    ) -> Dict[str, Any]:
        """
        Generates comprehensive MLOps training summary report.
        """
        return {
            "model_id": artifact.model_id,
            "version": artifact.version,
            "model_type": artifact.model_type,
            "created_at": artifact.created_at,
            "checksum": artifact.checksum,
            "metrics": {
                "accuracy": eval_report.accuracy,
                "precision": eval_report.precision,
                "recall": eval_report.recall,
                "f1_score": eval_report.f1_score,
                "roc_auc": eval_report.roc_auc
            },
            "confusion_matrix": eval_report.confusion_matrix,
            "feature_importance": eval_report.feature_importance,
            "champion_comparison": comparison.__dict__ if comparison else None
        }
