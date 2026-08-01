"""
RAHUUL RADAR — F&O Engine: Implied Volatility (IV) Engine (Task 9)
==================================================================
Calculates Implied Volatility metrics:
- Current IV
- IV Rank (IVR)
- IV Percentile (IVP)
- IV Expansion detection
- IV Crush risk detection
"""

from typing import Dict, Any, List
from core.fno_engine.fno_models import IVMetrics


class IVEngine:
    """
    Implied Volatility (IV) Analytics Engine.
    """

    def calculate_iv_metrics(
        self,
        current_iv: float,
        historical_iv_series: List[float] = None
    ) -> IVMetrics:
        """
        Calculates IV Rank, IV Percentile, IV Expansion, and IV Crush flags.
        """
        if not historical_iv_series or len(historical_iv_series) < 5:
            # Fallback baseline history
            historical_iv_series = [12.0, 14.0, 16.0, 18.0, 20.0, 22.0, current_iv]

        min_iv = min(historical_iv_series)
        max_iv = max(historical_iv_series)
        iv_range = max(max_iv - min_iv, 0.01)

        # IV Rank: (Current IV - Min IV) / (Max IV - Min IV) * 100
        iv_rank = round(min(max(((current_iv - min_iv) / iv_range) * 100.0, 0.0), 100.0), 2)

        # IV Percentile: % of historical IV values below current IV
        count_below = sum(1 for iv in historical_iv_series if iv < current_iv)
        iv_percentile = round((count_below / len(historical_iv_series)) * 100.0, 2)

        # IV Expansion: IV Rank > 70 or current IV 20% higher than historical mean
        mean_iv = sum(historical_iv_series) / len(historical_iv_series)
        iv_expansion = bool(iv_rank > 70.0 or current_iv > (mean_iv * 1.20))

        # IV Crush: IV Rank < 20 or post-event volatility collapse
        iv_crush = bool(iv_rank < 20.0 or current_iv < (mean_iv * 0.80))

        return IVMetrics(
            current_iv=round(current_iv, 2),
            iv_rank=iv_rank,
            iv_percentile=iv_percentile,
            iv_expansion=iv_expansion,
            iv_crush=iv_crush
        )
