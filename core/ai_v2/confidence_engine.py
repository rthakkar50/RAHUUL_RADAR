"""
RAHUUL RADAR — AI Engine V2: Confidence Engine (Task 4)
========================================================
Computes production confidence (0-100) using real-time factors:
1. Prediction probability
2. Feature completeness
3. Trend alignment
4. Volume quality
5. Market regime
6. Historical model baseline accuracy

Replaces training-score based static confidence.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("ConfidenceEngine")


class ConfidenceEngine:
    """
    Production-grade Confidence Calibration Engine.
    Ensures confidence is strictly bounded between 0 and 100.
    """

    def calculate_confidence(
        self,
        prediction_result: Dict[str, Any],
        features: Dict[str, float],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates calibrated confidence score (0-100).
        """
        signal = prediction_result.get("predicted_signal", "HOLD")
        probs = prediction_result.get("probabilities", {})
        
        # 1. Prediction Probability Component (Max 35 pts)
        signal_prob = probs.get(signal, 0.34) if signal in ("BUY", "SELL") else max(probs.values(), default=0.34)
        prob_score = min(35.0, signal_prob * 35.0)

        # 2. Feature Completeness Component (Max 15 pts)
        total_keys = len(features)
        valid_count = sum(1 for v in features.values() if v is not None and not (isinstance(v, float) and (v != v)))
        completeness_pct = valid_count / max(total_keys, 1)
        completeness_score = completeness_pct * 15.0

        # 3. Trend Alignment Component (Max 20 pts)
        close_price = features.get("ema_20", 100.0)
        ema_200 = features.get("ema_200", 95.0)
        trend_aligned = False
        if signal == "BUY" and close_price >= ema_200:
            trend_aligned = True
        elif signal == "SELL" and close_price <= ema_200:
            trend_aligned = True
        elif signal == "HOLD":
            trend_aligned = True
        trend_score = 20.0 if trend_aligned else 5.0

        # 4. Volume Quality Component (Max 15 pts)
        vol_ratio = features.get("volume_ratio", 1.0)
        if vol_ratio >= 1.5:
            vol_score = 15.0
        elif vol_ratio >= 1.0:
            vol_score = 10.0
        else:
            vol_score = 5.0

        # 5. Market Regime Component (Max 15 pts)
        regime = str(context_data.get("market_regime", "Neutral"))
        regime_aligned = False
        if signal == "BUY" and ("Bull" in regime or "Strong" in regime or "Neutral" in regime):
            regime_aligned = True
        elif signal == "SELL" and ("Bear" in regime or "Weak" in regime or "Neutral" in regime):
            regime_aligned = True
        elif signal == "HOLD":
            regime_aligned = True
        regime_score = 15.0 if regime_aligned else 5.0

        # Historical baseline accuracy weight multiplier (default 1.0)
        hist_accuracy_factor = float(context_data.get("historical_accuracy_factor", 1.0))

        raw_confidence = (prob_score + completeness_score + trend_score + vol_score + regime_score) * hist_accuracy_factor
        calibrated_confidence = round(min(max(raw_confidence, 0.0), 100.0), 1)

        return {
            "confidence": calibrated_confidence,
            "components": {
                "probability_score": round(prob_score, 1),
                "completeness_score": round(completeness_score, 1),
                "trend_score": round(trend_score, 1),
                "volume_score": round(vol_score, 1),
                "regime_score": round(regime_score, 1)
            },
            "trend_aligned": trend_aligned,
            "regime_aligned": regime_aligned
        }
