"""
RAHUUL RADAR — AI Learning Platform: Feature Dataset (Task 1)
==============================================================
Encapsulates features (X) and target labels (y) for offline model training.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from ai_learning.ai_learning_models import DatasetMetadata


class FeatureDataset:
    """
    Feature Matrix & Label Container for ML Training.
    """

    def __init__(self, X: np.ndarray, y: np.ndarray, feature_names: List[str], metadata: DatasetMetadata):
        self.X = X
        self.y = y
        self.feature_names = feature_names
        self.metadata = metadata

    @property
    def sample_count(self) -> int:
        return len(self.y)

    @property
    def feature_count(self) -> int:
        return len(self.feature_names)
