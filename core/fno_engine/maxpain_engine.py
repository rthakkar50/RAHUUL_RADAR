"""
RAHUUL RADAR — F&O Engine: Max Pain Engine (Task 7)
===================================================
Calculates Max Pain strike level, total pain distribution,
and option-derived Support and Resistance levels for Current, Next, and Monthly expiries.
"""

from typing import List, Dict, Any
from core.fno_engine.fno_models import MaxPainMetrics, OptionChainItem


class MaxPainEngine:
    """
    Max Pain & Key Support/Resistance Engine.
    """

    def calculate_max_pain(self, chain: List[OptionChainItem]) -> MaxPainMetrics:
        """
        Calculates Max Pain strike price where total loss to buyers is maximized.
        """
        if not chain:
            return MaxPainMetrics(max_pain_strike=0.0, total_pain=0.0, support_level=0.0, resistance_level=0.0)

        strikes = [item.strike_price for item in chain]
        min_pain = float("inf")
        max_pain_strike = strikes[0]

        for s_eval in strikes:
            current_pain = 0.0
            for item in chain:
                # Loss for Call Buyers if underlying expires at s_eval
                call_loss = max(s_eval - item.strike_price, 0.0) * item.call_oi
                # Loss for Put Buyers if underlying expires at s_eval
                put_loss = max(item.strike_price - s_eval, 0.0) * item.put_oi
                current_pain += (call_loss + put_loss)

            if current_pain < min_pain:
                min_pain = current_pain
                max_pain_strike = s_eval

        # Key Support: Highest Put OI Strike
        support_item = max(chain, key=lambda x: x.put_oi, default=chain[0])
        support_level = support_item.strike_price

        # Key Resistance: Highest Call OI Strike
        resistance_item = max(chain, key=lambda x: x.call_oi, default=chain[0])
        resistance_level = resistance_item.strike_price

        return MaxPainMetrics(
            max_pain_strike=max_pain_strike,
            total_pain=round(min_pain, 2),
            support_level=support_level,
            resistance_level=resistance_level
        )
