"""
RAHUUL RADAR — AI Engine V2: Explainable AI (Task 5)
=====================================================
Generates human-readable, transparent reasoning for every AI decision.
Transforms feature vectors and confidence factors into structured decision cards.
"""

from typing import Dict, Any, List


class ExplainableAI:
    """
    Explainable AI (XAI) engine for feature-driven signal rationale.
    """

    def explain(
        self,
        predicted_signal: str,
        confidence: float,
        features: Dict[str, float],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates structured explanation dictionary with clear bulleted reasons.
        """
        reasons = []
        positive_factors = []
        negative_factors = []

        rsi = features.get("rsi_14", 50.0)
        vol_ratio = features.get("volume_ratio", 1.0)
        mom = features.get("price_momentum", 0.0)
        rs = features.get("relative_strength", 50.0)
        breadth = features.get("market_breadth", 50.0)
        close_price = features.get("ema_20", 100.0)
        ema_200 = features.get("ema_200", 95.0)

        # 1. Trend Rationale
        if close_price > ema_200:
            msg = f"EMA Trend Bullish (Price ₹{close_price:.1f} above EMA200 ₹{ema_200:.1f})"
            positive_factors.append(msg)
            if predicted_signal == "BUY":
                reasons.append(msg)
        else:
            msg = f"EMA Trend Bearish (Price ₹{close_price:.1f} below EMA200 ₹{ema_200:.1f})"
            negative_factors.append(msg)
            if predicted_signal == "SELL":
                reasons.append(msg)

        # 2. RSI Rationale
        if rsi >= 60:
            msg = f"RSI Strong Bullish (RSI at {rsi:.1f})"
            positive_factors.append(msg)
            if predicted_signal == "BUY":
                reasons.append(msg)
        elif rsi <= 40:
            msg = f"RSI Oversold / Bearish (RSI at {rsi:.1f})"
            negative_factors.append(msg)
            if predicted_signal == "SELL":
                reasons.append(msg)

        # 3. Volume Rationale
        if vol_ratio >= 1.5:
            msg = f"Volume Increasing (Volume Ratio {vol_ratio:.1f}x)"
            positive_factors.append(msg)
            reasons.append(msg)
        elif vol_ratio < 0.8:
            msg = f"Volume Subdued (Volume Ratio {vol_ratio:.1f}x)"
            negative_factors.append(msg)

        # 4. Momentum Rationale
        if mom > 0:
            msg = f"Momentum Positive (+{mom:.1f}%)"
            positive_factors.append(msg)
            if predicted_signal == "BUY":
                reasons.append(msg)
        else:
            msg = f"Momentum Negative ({mom:.1f}%)"
            negative_factors.append(msg)
            if predicted_signal == "SELL":
                reasons.append(msg)

        # 5. Relative Strength & Market Breadth
        if rs >= 70:
            msg = f"Relative Strength Superior (RS Score {rs:.0f})"
            positive_factors.append(msg)
            reasons.append(msg)

        if breadth >= 60:
            msg = f"Market Breadth Positive ({breadth:.0f}% Advance Bias)"
            positive_factors.append(msg)
            reasons.append(msg)

        # Ensure fallback reasons if empty
        if not reasons:
            if predicted_signal == "BUY":
                reasons.append("Technical Indicators & Volume Alignment Favorable")
            elif predicted_signal == "SELL":
                reasons.append("Technical Resistance & Momentum Weakness Detected")
            else:
                reasons.append("Consolidation Range - Awaiting Clear Breakout Signal")

        return {
            "decision": predicted_signal,
            "confidence": confidence,
            "reasons": reasons,
            "positive_factors": positive_factors,
            "negative_factors": negative_factors,
            "example_format": f"{predicted_signal} | Confidence {confidence}% | Reason: " + ", ".join(reasons[:3])
        }
