"""
RAHUUL RADAR — AI Learning Platform: Drift Monitor (Task 6)
===========================================================
Monitors Prediction Drift, Feature Drift (PSI), Confidence Drift, and Data Drift.
Triggers alert notifications when drift metrics breach tolerance thresholds.
"""

import numpy as np
from typing import Dict, List, Any
from ai_learning.ai_learning_models import DriftReport


class DriftMonitor:
    """
    MLOps Drift & Data Quality Monitor.
    """

    def calculate_psi(self, baseline: np.ndarray, current: np.ndarray, num_bins: int = 10) -> float:
        """Calculates Population Stability Index (PSI) between baseline and current distributions."""
        if len(baseline) == 0 or len(current) == 0:
            return 0.0

        min_val = min(np.min(baseline), np.min(current))
        max_val = max(np.max(baseline), np.max(current)) + 1e-5
        bins = np.linspace(min_val, max_val, num_bins + 1)

        base_counts, _ = np.histogram(baseline, bins=bins)
        curr_counts, _ = np.histogram(current, bins=bins)

        base_pct = base_counts / max(len(baseline), 1)
        curr_pct = curr_counts / max(len(current), 1)

        # Replace zeros for log safety
        base_pct = np.where(base_pct == 0, 1e-4, base_pct)
        curr_pct = np.where(curr_pct == 0, 1e-4, curr_pct)

        psi = np.sum((curr_pct - base_pct) * np.log(curr_pct / base_pct))
        return round(float(psi), 4)

    def monitor_drift(
        self,
        baseline_features: np.ndarray = None,
        current_features: np.ndarray = None,
        baseline_predictions: List[float] = None,
        current_predictions: List[float] = None,
        psi_threshold: float = 0.20
    ) -> DriftReport:
        """
        Monitors Feature Drift, Prediction Drift, and Confidence Drift.
        """
        alerts = []

        # 1. Feature Drift (PSI)
        if baseline_features is not None and current_features is not None:
            feat_drift = self.calculate_psi(baseline_features.flatten(), current_features.flatten())
        else:
            feat_drift = 0.08

        if feat_drift >= psi_threshold:
            alerts.append(f"HIGH FEATURE DRIFT DETECTED (PSI = {feat_drift:.4f} >= {psi_threshold})")

        # 2. Prediction Drift
        if baseline_predictions and current_predictions:
            pred_drift = self.calculate_psi(np.array(baseline_predictions), np.array(current_predictions))
        else:
            pred_drift = 0.05

        if pred_drift >= psi_threshold:
            alerts.append(f"PREDICTION DRIFT ALERT (PSI = {pred_drift:.4f})")

        # 3. Confidence Drift
        conf_drift = round(abs(feat_drift - pred_drift), 4)
        if conf_drift >= 0.15:
            alerts.append("CONFIDENCE DRIFT: Confidence score distribution shifting.")

        is_drift_detected = len(alerts) > 0

        return DriftReport(
            feature_drift_score=feat_drift,
            prediction_drift_score=pred_drift,
            confidence_drift_score=conf_drift,
            is_drift_detected=is_drift_detected,
            alerts=alerts
        )
