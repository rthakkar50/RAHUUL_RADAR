import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("IntradayQualityGate")

class IntradayQualityGate:
    """
    SPRINT-91: Institutional Quality Gate for Active Trading Scanner.
    Ensures only high-quality A+ setups pass through for intraday trading.
    Rejects weak opportunities immediately.
    """

    @staticmethod
    def evaluate(result: Dict[str, Any], market_context: Dict[str, Any] = None) -> Tuple[bool, str, float, list, str]:
        """
        Applies a calibrated institutional quality gate on the RankingEngine output.
        Incorporates Market Intelligence layer for overarching market regime filtering.
        Returns: (passed, signal_classification, custom_score, custom_reasons, rejection_reason)
        """
        if not result or result.get("status") != "RANKED":
            return False, "REJECT", 0.0, [], "Invalid or unranked result"

        direction = result.get("direction", "UNKNOWN")
        if direction not in ["BULLISH", "BEARISH"]:
            return False, "REJECT", 0.0, [], "Sideways"

        engines = result.get("engine_breakdown", {})
        metrics = result.get("debug_metrics", {})
        market_context = market_context or {}
        
        custom_score = 0.0
        custom_reasons = []
        rejection_factors = []

        # 1. Trend & EMA (25 pts)
        if engines.get("Trend", {}).get("Score Contribution", 0) > 5.0:
            custom_score += 25
            trend_str = "Bullish" if direction == "BULLISH" else "Bearish"
            custom_reasons.append(f"✓ {trend_str} Trend")
        else:
            rejection_factors.append("Weak Trend")

        # 2. Momentum (15 pts)
        if engines.get("Momentum", {}).get("Score Contribution", 0) > 2.5:
            custom_score += 15
            custom_reasons.append("✓ Strong Momentum")
        else:
            rejection_factors.append("Weak Momentum")

        # 3. Sector Strength (10 pts)
        sym_sector = result.get("sector", "UNKNOWN")
        strongest = market_context.get("strongest_sectors", [])
        weakest = market_context.get("weakest_sectors", [])
        
        if direction == "BULLISH" and any(s for s in strongest if s in sym_sector or sym_sector in s):
            custom_score += 10
            custom_reasons.append("✓ Strong Sector Tailwind")
        elif direction == "BEARISH" and any(s for s in weakest if s in sym_sector or sym_sector in s):
            custom_score += 10
            custom_reasons.append("✓ Weak Sector Tailwind")

        # 4. Relative Strength (10 pts)
        rs_score = engines.get("Relative Strength", {}).get("Score Contribution", 0)
        if rs_score > 2.5:
            custom_score += 10
            custom_reasons.append("✓ Outperforming NIFTY" if direction == "BULLISH" else "✓ Underperforming NIFTY")

        # 5. Volume Improvements (15 pts)
        vol = metrics.get("Volume", 0)
        vol_ma = metrics.get("Vol_MA20", 1)
        rel_vol = vol / vol_ma if vol_ma > 0 else 0
        
        if rel_vol > 2.0:
            custom_score += 15
            custom_reasons.append("✓ Volume Spike")
        elif rel_vol > 1.2:
            custom_score += 10
            custom_reasons.append("✓ Strong Relative Volume")
        else:
            rejection_factors.append("Low Volume")

        # 6. VWAP (10 pts)
        if engines.get("VWAP", {}).get("Score Contribution", 0) > 2.5:
            custom_score += 10
            vwap_str = "Above" if direction == "BULLISH" else "Below"
            custom_reasons.append(f"✓ {vwap_str} VWAP")
        else:
            rejection_factors.append("Poor VWAP Structure")

        # 7. Structure (10 pts)
        if engines.get("ICT", {}).get("Score Contribution", 0) > 0:
            custom_score += 10
            custom_reasons.append("✓ Institutional Structure")

        # 8. Risk Reward (5 pts)
        if engines.get("Risk Reward", {}).get("Score Contribution", 0) > 2.5:
            custom_score += 5
            custom_reasons.append("✓ Good Risk Reward")

        # --- MARKET REGIME MODIFIERS ---
        # The penalty is preserved here, as Quality Gate ignores RankingEngine's composite score.
        regime = market_context.get("regime", "Sideways")
        if regime == "Bear Trend" and direction == "BULLISH":
            custom_score -= 15  # Heavy penalty for fighting the trend
            rejection_factors.append("Fighting Bear Market")
        elif regime == "Bull Trend" and direction == "BEARISH":
            custom_score -= 15
            rejection_factors.append("Fighting Bull Market")
            
        if regime == "High Volatility":
            if rel_vol < 1.5:  # Demand higher volume during high volatility to trust the move
                custom_score -= 10
                rejection_factors.append("Low Vol in High VIX")

        # Signal Classification based on SPRINT-94 Score
        if custom_score >= 65:
            signal = "BUY" if direction == "BULLISH" else "SELL"
        elif custom_score >= 40:
            signal = "WATCH"
        else:
            dominant_reason = " | ".join(rejection_factors[:2]) if rejection_factors else "Score below 40"
            return False, "REJECT", custom_score, [], dominant_reason

        # Generate Explanation and Next Trigger (SPRINT-95)
        explanations = []
        triggers = []
        
        trend_dir = "Bullish" if direction == "BULLISH" else "Bearish"
        if "Weak Trend" not in rejection_factors:
            explanations.append(f"• {trend_dir} trend confirmed")
        else:
            explanations.append(f"• {trend_dir} trend not fully confirmed")
            
        explanations.append(f"• Confidence only {result.get('confidence', 0)}%" if signal == "WATCH" else f"• Confidence {result.get('confidence', 0)}%")
        
        if signal == "WATCH":
            if "Low Volume" in rejection_factors or "Low Vol in High VIX" in rejection_factors:
                explanations.append("• Relative Volume below threshold")
                triggers.append("RVOL > 1.5")
            if "Poor VWAP Structure" in rejection_factors:
                explanations.append("• Waiting for VWAP breakout" if direction == "BULLISH" else "• Waiting for VWAP breakdown")
                triggers.append("price closes above VWAP" if direction == "BULLISH" else "price closes below VWAP")
            if "Weak Momentum" in rejection_factors:
                explanations.append("• Momentum not yet confirmed")
                triggers.append("momentum expansion")
                
            if not triggers:
                triggers.append("structural confirmation")
                
            trigger_text = f"If {' and '.join(triggers)}, upgrade to {'BUY' if direction == 'BULLISH' else 'SELL'}."
        else:
            explanations.append("• Entry confirmed")
            trigger_text = "Ready for execution."

        result["explanation"] = "\n".join(explanations)
        result["next_trigger"] = trigger_text

        return True, signal, custom_score, custom_reasons, ""
