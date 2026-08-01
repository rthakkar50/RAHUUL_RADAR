"""
RAHUUL RADAR — F&O Engine: PCR Engine (Task 6)
==============================================
Calculates Put-Call Ratios:
- Total PCR (Total Put OI / Total Call OI)
- Strike PCR (Strike specific Put OI / Call OI)
- Weighted PCR (Volume-weighted PCR)
- Historical PCR
"""

from typing import Dict, List, Any
from core.fno_engine.fno_models import PCRMetrics, OptionChainItem


class PCREngine:
    """
    Put-Call Ratio (PCR) Metrics Calculator.
    """

    def calculate_pcr(self, chain: List[OptionChainItem], target_strike: float = 0.0) -> PCRMetrics:
        """
        Calculates Total PCR, Strike PCR, Weighted PCR, and Historical PCR.
        """
        if not chain:
            return PCRMetrics(total_pcr=1.0, strike_pcr=1.0, weighted_pcr=1.0, historical_pcr=1.0)

        total_call_oi = sum(item.call_oi for item in chain)
        total_put_oi = sum(item.put_oi for item in chain)
        
        total_pcr = round(total_put_oi / max(total_call_oi, 1), 2)

        # Strike PCR at target_strike or ATM
        strike_pcr = total_pcr
        if target_strike > 0:
            for item in chain:
                if abs(item.strike_price - target_strike) < 1.0:
                    strike_pcr = round(item.put_oi / max(item.call_oi, 1), 2)
                    break

        # Weighted PCR (Volume weighted)
        weighted_call = sum(item.call_oi * item.call_volume for item in chain)
        weighted_put = sum(item.put_oi * item.put_volume for item in chain)
        weighted_pcr = round(weighted_put / max(weighted_call, 1), 2) if weighted_call > 0 else total_pcr

        # Historical baseline approximation
        historical_pcr = round((total_pcr + weighted_pcr) / 2.0, 2)

        return PCRMetrics(
            total_pcr=total_pcr,
            strike_pcr=strike_pcr,
            weighted_pcr=weighted_pcr,
            historical_pcr=historical_pcr
        )
