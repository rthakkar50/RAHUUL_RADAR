"""
RAHUUL RADAR — AI Learning Platform: Champion-Challenger Engine (Task 4)
========================================================================
Compares Champion vs Challenger model metrics side-by-side.
"""

from typing import Dict, Any, Optional
from ai_learning.ai_learning_models import ChampionChallengerComparison, ModelArtifact
from ai_learning.model_registry import ModelRegistry


class ChampionChallengerEngine:
    """
    Champion vs Challenger Performance Comparison Engine.
    """

    def __init__(self, registry: Optional[ModelRegistry] = None):
        self.registry = registry or ModelRegistry.get_instance()

    def compare_models(
        self,
        challenger_version: str,
        challenger_metrics: Dict[str, float]
    ) -> ChampionChallengerComparison:
        """
        Compares candidate challenger model against active production champion model.
        """
        champ_meta = self.registry.get_champion()
        champ_version = champ_meta.get("version", "AI_v2")
        champ_metrics = champ_meta.get("metrics", {"accuracy": 82.5, "profit_factor": 2.8, "max_drawdown": 3.2, "sharpe": 2.6})

        diffs = {
            "accuracy_diff": round(challenger_metrics.get("accuracy", 0.0) - champ_metrics.get("accuracy", 0.0), 2),
            "profit_factor_diff": round(challenger_metrics.get("profit_factor", 0.0) - champ_metrics.get("profit_factor", 0.0), 2),
            "max_drawdown_diff": round(challenger_metrics.get("max_drawdown", 0.0) - champ_metrics.get("max_drawdown", 0.0), 2),
            "sharpe_diff": round(challenger_metrics.get("sharpe", 0.0) - champ_metrics.get("sharpe", 0.0), 2)
        }

        # Recommendation logic
        rationale = []
        is_better = True

        if diffs["accuracy_diff"] <= 0:
            rationale.append(f"Accuracy did not improve ({diffs['accuracy_diff']}%)")
            is_better = False
        else:
            rationale.append(f"Accuracy improved by +{diffs['accuracy_diff']}%")

        if diffs["max_drawdown_diff"] > 0:
            rationale.append(f"Max Drawdown increased by +{diffs['max_drawdown_diff']}% (Must decrease)")
            is_better = False
        else:
            rationale.append("Max Drawdown controlled/reduced")

        winner = challenger_version if is_better else champ_version

        return ChampionChallengerComparison(
            champion_version=champ_version,
            challenger_version=challenger_version,
            champion_metrics=champ_metrics,
            challenger_metrics=challenger_metrics,
            metric_diffs=diffs,
            recommended_winner=winner,
            rationale=rationale
        )
