"""
RAHUUL RADAR — AI Learning Platform: Promotion Manager (Task 5 & Task 9)
========================================================================
Enforces strict promotion rules and safety gates for model deployment.
Requires explicit approval — zero automatic live model deployment.
"""

import logging
from typing import Dict, Any, Optional
from ai_learning.ai_learning_models import PromotionDecision
from ai_learning.champion_challenger import ChampionChallengerEngine
from ai_learning.model_registry import ModelRegistry

logger = logging.getLogger("PromotionManager")


class ModelPromotionManager:
    """
    Enforces MLOps Promotion Gateways & Safety Requirements.
    """

    def __init__(
        self,
        cmp_engine: Optional[ChampionChallengerEngine] = None,
        registry: Optional[ModelRegistry] = None
    ):
        self.cmp_engine = cmp_engine or ChampionChallengerEngine()
        self.registry = registry or ModelRegistry.get_instance()

    def evaluate_promotion_eligibility(
        self,
        challenger_version: str,
        challenger_metrics: Dict[str, float],
        walk_forward_stability: float = 0.85,
        explicit_approval: bool = False
    ) -> PromotionDecision:
        """
        Evaluates candidate challenger model against strict promotion rules:
        1. Accuracy must improve.
        2. Drawdown must decrease.
        3. Profit Factor must improve.
        4. Walk-Forward stability >= 0.70.
        5. Explicit approval required (Task 9: Safety).
        """
        comparison = self.cmp_engine.compare_models(challenger_version, challenger_metrics)
        diffs = comparison.metric_diffs

        rejection_reasons = []

        # Rule 1: Accuracy
        if diffs["accuracy_diff"] <= 0:
            rejection_reasons.append(f"Accuracy did not improve (Diff: {diffs['accuracy_diff']}%)")

        # Rule 2: Max Drawdown
        if diffs["max_drawdown_diff"] > 0:
            rejection_reasons.append(f"Max Drawdown increased by {diffs['max_drawdown_diff']}%")

        # Rule 3: Profit Factor
        if diffs["profit_factor_diff"] < 0:
            rejection_reasons.append(f"Profit Factor degraded by {diffs['profit_factor_diff']}")

        # Rule 4: Walk-Forward Stability
        if walk_forward_stability < 0.70:
            rejection_reasons.append(f"Walk-Forward Stability ({walk_forward_stability}) below 0.70 threshold")

        # Rule 5: Explicit Approval Gate (Task 9)
        if not explicit_approval:
            rejection_reasons.append("Safety Violation: Explicit human/CTO approval required for model promotion.")

        is_approved = (len(rejection_reasons) == 0)

        return PromotionDecision(
            challenger_version=challenger_version,
            is_approved=is_approved,
            rejection_reasons=rejection_reasons,
            evaluation_summary={
                "champion_version": comparison.champion_version,
                "challenger_version": challenger_version,
                "diffs": diffs,
                "walk_forward_stability": walk_forward_stability,
                "explicit_approval": explicit_approval
            }
        )

    def execute_promotion(self, challenger_version: str, explicit_approval: bool = False) -> bool:
        """Executes model promotion in registry ONLY IF explicit approval is True."""
        if not explicit_approval:
            logger.warning("Promotion rejected: Explicit approval missing!")
            return False

        return self.registry.set_champion(challenger_version)
