"""
RAHUUL RADAR — F&O Engine: Open Interest (OI) Engine (Task 5)
=============================================================
Calculates Open Interest Build-Up patterns:
- Long Build-Up (Price UP, Change in OI UP)
- Short Build-Up (Price DOWN, Change in OI UP)
- Short Covering (Price UP, Change in OI DOWN)
- Long Unwinding (Price DOWN, Change in OI DOWN)
Computes OI Momentum & OI Trend indicators.
"""

from typing import Dict, Any, List
from core.fno_engine.fno_models import OIBuildUp, OptionChainItem


class OIEngine:
    """
    Open Interest Analysis & Trend Engine.
    """

    def analyze_buildup(self, price_change: float, oi_change: float) -> OIBuildUp:
        """
        Classifies OI Build-up category based on price change and OI change.
        """
        if price_change > 0 and oi_change > 0:
            return OIBuildUp.LONG_BUILDUP
        elif price_change < 0 and oi_change > 0:
            return OIBuildUp.SHORT_BUILDUP
        elif price_change > 0 and oi_change < 0:
            return OIBuildUp.SHORT_COVERING
        elif price_change < 0 and oi_change < 0:
            return OIBuildUp.LONG_UNWINDING
        return OIBuildUp.NEUTRAL

    def calculate_oi_metrics(self, chain: List[OptionChainItem], price_change_pct: float = 0.5) -> Dict[str, Any]:
        """
        Computes aggregated Call/Put OI build-up metrics, OI momentum, and OI trend.
        """
        total_call_oi = sum(item.call_oi for item in chain)
        total_put_oi = sum(item.put_oi for item in chain)
        total_call_chg = sum(item.call_change_oi for item in chain)
        total_put_chg = sum(item.put_change_oi for item in chain)

        call_buildup = self.analyze_buildup(price_change_pct, total_call_chg)
        put_buildup = self.analyze_buildup(-price_change_pct, total_put_chg)

        # OI Momentum score (0 to 100)
        net_oi_chg = total_put_chg - total_call_chg
        total_chg_abs = max(abs(total_put_chg) + abs(total_call_chg), 1)
        oi_momentum = round(min(max(50.0 + (net_oi_chg / total_chg_abs) * 50.0, 0.0), 100.0), 1)

        # OI Trend Classification
        if oi_momentum >= 65.0:
            oi_trend = "BULLISH_OI"
        elif oi_momentum <= 35.0:
            oi_trend = "BEARISH_OI"
        else:
            oi_trend = "NEUTRAL_OI"

        return {
            "total_call_oi": total_call_oi,
            "total_put_oi": total_put_oi,
            "total_call_change_oi": total_call_chg,
            "total_put_change_oi": total_put_chg,
            "call_buildup": call_buildup.value,
            "put_buildup": put_buildup.value,
            "oi_momentum": oi_momentum,
            "oi_trend": oi_trend
        }
