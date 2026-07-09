from typing import Dict
from option_chain.synthetic_chain import SyntheticOptionChain
from option_chain.oi_analyzer import OIAnalyzer
from option_chain.pcr_analyzer import PCRAnalyzer
from option_chain.iv_analyzer import IVAnalyzer
from option_chain.strike_selector import StrikeSelector

class OptionChainEngine:
    def __init__(self, symbol: str, underlying_price: float, atr: float = 150.0):
        self.symbol = symbol
        self.underlying_price = underlying_price
        # Using synthetic chain until real API is plugged in
        self.generator = SyntheticOptionChain(symbol, underlying_price, atr)

    def generate_full_analysis(self, market_trend: str = "BULLISH") -> Dict:
        """
        Fetches chain and orchestrates the full Option Intelligence analysis.
        """
        chain = self.generator.get_full_chain()
        
        oi_data = OIAnalyzer.analyze(chain)
        pcr_data = PCRAnalyzer.analyze(chain)
        iv_data = IVAnalyzer.analyze(chain)
        strike_data = StrikeSelector.select_strikes(chain, market_trend)
        
        # V2.0 Option Radar Score (0-100)
        # Weight example: Trend(20), OI(20), PCR(15), Vol(15), IV(10), Momentum(20)
        score = 0
        if market_trend in ["BULLISH", "STRONG_BULLISH"]: score += 20
        
        if pcr_data["sentiment"] in ["BULLISH", "STRONG BULLISH"]: score += 15
        elif pcr_data["sentiment"] == "NEUTRAL": score += 7
        
        if oi_data["buildup_bias"] == "BULLISH": score += 20
        elif oi_data["buildup_bias"] == "NEUTRAL": score += 10
        
        # Volume and Momentum are approximated here as synthetic logic guarantees decent volume
        score += 15 # Volume
        score += 15 # Momentum
        
        if iv_data["iv_risk"] == "LOW": score += 10
        elif iv_data["iv_risk"] == "MEDIUM": score += 5
        
        # Generate overall bias
        if score >= 80:
            overall_bias = "STRONG CALL BUY"
        elif score >= 60:
            overall_bias = "CALL BUY"
        elif score <= 40:
            overall_bias = "PUT BUY"
        else:
            overall_bias = "NEUTRAL"
            
        return {
            "symbol": self.symbol,
            "expiry": chain["expiry"],
            "underlying_price": self.underlying_price,
            "chain_data": chain,
            "oi_analysis": oi_data,
            "pcr_analysis": pcr_data,
            "iv_analysis": iv_data,
            "strike_selection": strike_data,
            "radar_score": score,
            "overall_bias": overall_bias
        }
