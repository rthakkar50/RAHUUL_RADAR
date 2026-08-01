"""
RAHUUL RADAR — Enterprise AI Learning Platform: Domain Models
=============================================================
Data contracts and MLOps domain models for AI model training and evaluation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime


@dataclass
class DatasetMetadata:
    dataset_id: str
    sample_count: int
    feature_count: int
    created_at: str
    sources: List[str] = field(default_factory=list)


@dataclass
class ModelArtifact:
    model_id: str
    version: str
    model_type: str  # RANDOM_FOREST / LOGISTIC_REGRESSION / GRADIENT_BOOSTING
    created_at: str
    checksum: str
    metrics: Dict[str, float]
    artifact_path: str
    is_champion: bool = False


@dataclass
class EvaluationReport:
    model_id: str
    version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    confusion_matrix: List[List[int]]
    feature_importance: Dict[str, float]


@dataclass
class ChampionChallengerComparison:
    champion_version: str
    challenger_version: str
    champion_metrics: Dict[str, float]
    challenger_metrics: Dict[str, float]
    metric_diffs: Dict[str, float]
    recommended_winner: str
    rationale: List[str]


@dataclass
class DriftReport:
    feature_drift_score: float
    prediction_drift_score: float
    confidence_drift_score: float
    is_drift_detected: bool
    alerts: List[str] = field(default_factory=list)


@dataclass
class PromotionDecision:
    challenger_version: str
    is_approved: bool
    rejection_reasons: List[str] = field(default_factory=list)
    evaluation_summary: Dict[str, Any] = field(default_factory=dict)
