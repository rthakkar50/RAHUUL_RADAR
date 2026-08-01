"""
RAHUUL RADAR — F&O Engine: Contract Selector (Task 3)
=====================================================
Selects ATM, ITM, OTM, Deep ITM, and Deep OTM strikes for Call/Put contracts
based on underlying spot price and step configuration.
"""

import math
from typing import Dict, Any, List, Optional


class ContractSelector:
    """
    Automated Strike & Contract Selection Engine.
    """

    def get_atm_strike(self, spot_price: float, step: float = 50.0) -> float:
        """Calculates nearest At-The-Money (ATM) strike price."""
        if step <= 0:
            step = 50.0
        return round(round(spot_price / step) * step, 2)

    def select_strike(
        self,
        spot_price: float,
        option_type: str,
        strike_type: str = "ATM",
        distance: int = 1,
        step: float = 50.0
    ) -> float:
        """
        Selects target strike based on strike_type:
        - ATM: At-The-Money
        - ITM: In-The-Money (1 step)
        - DEEP_ITM: Deep In-The-Money (distance steps)
        - OTM: Out-Of-The-Money (1 step)
        - DEEP_OTM: Deep Out-Of-The-Money (distance steps)
        """
        atm = self.get_atm_strike(spot_price, step)
        strike_type_upper = strike_type.upper()
        option_type_upper = option_type.upper()
        offset = distance * step

        if strike_type_upper == "ATM":
            return atm

        if option_type_upper in ("CE", "CALL"):
            if strike_type_upper in ("ITM", "IN_THE_MONEY"):
                return atm - (1 * step)
            elif strike_type_upper in ("DEEP_ITM", "DEEP_IN_THE_MONEY"):
                return atm - offset
            elif strike_type_upper in ("OTM", "OUT_OF_THE_MONEY"):
                return atm + (1 * step)
            elif strike_type_upper in ("DEEP_OTM", "DEEP_OUT_OF_THE_MONEY"):
                return atm + offset
        else: # PE / PUT
            if strike_type_upper in ("ITM", "IN_THE_MONEY"):
                return atm + (1 * step)
            elif strike_type_upper in ("DEEP_ITM", "DEEP_IN_THE_MONEY"):
                return atm + offset
            elif strike_type_upper in ("OTM", "OUT_OF_THE_MONEY"):
                return atm - (1 * step)
            elif strike_type_upper in ("DEEP_OTM", "DEEP_OUT_OF_THE_MONEY"):
                return atm - offset

        return atm

    def get_strike_chain_range(
        self,
        spot_price: float,
        step: float = 50.0,
        num_strikes_above_below: int = 10
    ) -> List[float]:
        """Returns a list of strike prices centered around ATM."""
        atm = self.get_atm_strike(spot_price, step)
        strikes = []
        for i in range(-num_strikes_above_below, num_strikes_above_below + 1):
            strikes.append(round(atm + (i * step), 2))
        return strikes
