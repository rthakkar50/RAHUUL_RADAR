import random
from typing import List, Dict
from datetime import datetime, timedelta

class SyntheticOptionChain:
    """
    Generates realistic Option Chain data (Premiums, OI, Volume, IV) based on 
    the live underlying index price, bypassing the need for a paid options API.
    """
    def __init__(self, symbol: str, underlying_price: float, atr: float = 150.0):
        self.symbol = symbol
        self.underlying_price = underlying_price
        self.atr = atr
        self.step = 100 if "BANK" in symbol else 50
        
    def generate_strikes(self) -> List[Dict]:
        """
        Generates 5 ITM, 1 ATM, and 5 OTM strikes.
        """
        atm_strike = round(self.underlying_price / self.step) * self.step
        strikes = []
        
        for i in range(-5, 6):
            strike = atm_strike + (i * self.step)
            
            # Distance from ATM influences premium, OI, and IV
            distance = abs(i)
            
            # Calls
            ce_itm = i < 0
            ce_intrinsic = max(0, self.underlying_price - strike)
            ce_time_value = max(10, self.atr * (1 - (distance * 0.15))) * random.uniform(0.9, 1.1)
            ce_premium = round(ce_intrinsic + ce_time_value, 2)
            
            ce_oi = int(1000000 / (distance + 1)) + random.randint(-50000, 50000)
            ce_oi_change = int(ce_oi * random.uniform(-0.1, 0.3))
            ce_vol = int(ce_oi * random.uniform(0.5, 2.0))
            ce_iv = round(random.uniform(12.0, 25.0) + (distance * 0.5), 2)
            
            # Puts
            pe_itm = i > 0
            pe_intrinsic = max(0, strike - self.underlying_price)
            pe_time_value = max(10, self.atr * (1 - (distance * 0.15))) * random.uniform(0.9, 1.1)
            pe_premium = round(pe_intrinsic + pe_time_value, 2)
            
            pe_oi = int(1000000 / (distance + 1)) + random.randint(-50000, 50000)
            pe_oi_change = int(pe_oi * random.uniform(-0.1, 0.3))
            pe_vol = int(pe_oi * random.uniform(0.5, 2.0))
            pe_iv = round(random.uniform(12.0, 25.0) + (distance * 0.5), 2)
            
            strikes.append({
                "strike": strike,
                "CE": {
                    "premium": ce_premium,
                    "oi": max(0, ce_oi),
                    "oi_change": ce_oi_change,
                    "volume": max(0, ce_vol),
                    "iv": ce_iv,
                    "type": "ITM" if ce_itm else "ATM" if i == 0 else "OTM"
                },
                "PE": {
                    "premium": pe_premium,
                    "oi": max(0, pe_oi),
                    "oi_change": pe_oi_change,
                    "volume": max(0, pe_vol),
                    "iv": pe_iv,
                    "type": "ITM" if pe_itm else "ATM" if i == 0 else "OTM"
                }
            })
            
        return strikes
        
    def get_full_chain(self) -> Dict:
        """
        Returns a complete mocked option chain payload.
        """
        return {
            "symbol": self.symbol,
            "underlying_price": self.underlying_price,
            "expiry": (datetime.now() + timedelta(days=4)).strftime("%d-%b-%Y"),
            "timestamp": datetime.now().isoformat(),
            "strikes": self.generate_strikes()
        }
