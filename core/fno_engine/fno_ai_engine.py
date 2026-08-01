"""
RAHUUL RADAR — F&O Engine: AI Decision Engine (Task 10)
======================================================
Dedicated Derivatives AI Decision Engine.
Evaluates Trend, VWAP, EMA, OI, PCR, Max Pain, IV, Greeks, Market Breadth, Volume, Momentum.
Outputs Action (BUY, SELL, WAIT), Confidence (0-100), and Rationale.
"""

from typing import Dict, Any, List
from core.fno_engine.fno_models import Greeks, IVMetrics, PCRMetrics, MaxPainMetrics, OIBuildUp


class FNOAIEngine:
    """
    Dedicated AI Engine for Option & Futures Signal Generation.
    """

    def evaluate_derivatives_signal(
        self,
        symbol: str,
        spot_price: float,
        vwap: float,
        ema_20: float,
        ema_200: float,
        oi_metrics: Dict[str, Any],
        pcr_metrics: PCRMetrics,
        max_pain_metrics: MaxPainMetrics,
        iv_metrics: IVMetrics,
        greeks: Greeks,
        market_breadth: float = 60.0,
        volume_ratio: float = 1.5,
        momentum_score: float = 70.0
    ) -> Dict[str, Any]:
        """
        Synthesizes technical, quantitative derivative factors into a decision.
        """
        reasons = []
        bullish_pts = 0.0
        bearish_pts = 0.0

        # 1. Trend & Moving Averages
        if spot_price > ema_20:
            bullish_pts += 15.0
            reasons.append(f"Price ₹{spot_price:.1f} above 20 EMA ₹{ema_20:.1f}")
        else:
            bearish_pts += 15.0
            reasons.append(f"Price ₹{spot_price:.1f} below 20 EMA ₹{ema_20:.1f}")

        # 2. VWAP Alignment
        if spot_price > vwap:
            bullish_pts += 15.0
            reasons.append(f"Price above VWAP ₹{vwap:.1f}")
        else:
            bearish_pts += 15.0
            reasons.append(f"Price below VWAP ₹{vwap:.1f}")

        # 3. PCR Signal
        pcr = pcr_metrics.total_pcr
        if pcr >= 1.2:
            bullish_pts += 15.0
            reasons.append(f"Bullish PCR Ratio ({pcr:.2f})")
        elif pcr <= 0.7:
            bearish_pts += 15.0
            reasons.append(f"Bearish PCR Ratio ({pcr:.2f})")

        # 4. Open Interest (OI) Trend
        oi_trend = oi_metrics.get("oi_trend", "NEUTRAL_OI")
        call_buildup = oi_metrics.get("call_buildup", "NEUTRAL")
        if oi_trend == "BULLISH_OI" or call_buildup == OIBuildUp.SHORT_COVERING.value:
            bullish_pts += 20.0
            reasons.append(f"Bullish OI Structure ({oi_metrics.get('oi_momentum', 50)}% Momentum)")
        elif oi_trend == "BEARISH_OI" or call_buildup == OIBuildUp.SHORT_BUILDUP.value:
            bearish_pts += 20.0
            reasons.append("Bearish OI Structure (Short Build-Up)")

        # 5. Max Pain & Support Level
        max_pain = max_pain_metrics.max_pain_strike
        if spot_price < max_pain:
            bullish_pts += 10.0
            reasons.append(f"Spot below Max Pain ₹{max_pain:.0f} (Pull-up expected)")
        else:
            bearish_pts += 10.0

        # 6. IV & Greeks
        if iv_metrics.iv_expansion:
            reasons.append("IV Expansion Active (Options Premium Inflated)")
        if greeks.delta > 0.40:
            reasons.append(f"Optimal Option Delta ({greeks.delta:.2f})")

        # 7. Volume & Breadth
        if volume_ratio >= 1.2:
            bullish_pts += 15.0
            reasons.append(f"Strong Derivatives Volume ({volume_ratio:.1f}x)")

        # Decision Threshold Resolution
        total_pts = bullish_pts + bearish_pts
        if bullish_pts >= 55.0 and bullish_pts > bearish_pts:
            action = "BUY"
            raw_confidence = (bullish_pts / max(total_pts, 1.0)) * 100.0
        elif bearish_pts >= 55.0 and bearish_pts > bullish_pts:
            action = "SELL"
            raw_confidence = (bearish_pts / max(total_pts, 1.0)) * 100.0
        else:
            action = "WAIT"
            raw_confidence = 50.0

        calibrated_confidence = round(min(max(raw_confidence, 0.0), 100.0), 1)

        return {
            "action": action,
            "confidence": calibrated_confidence,
            "reasons": reasons,
            "bullish_points": bullish_pts,
            "bearish_points": bearish_pts
        }
