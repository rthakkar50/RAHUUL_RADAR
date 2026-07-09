from typing import Dict
import pandas as pd
import math

class MarketIntelligenceEngine:
    """
    MARKET INTELLIGENCE ENGINE (MIE) V2.0
    Top-Level Market Evaluator. Runs before any stock is scanned.
    Mission: Dictate trading aggressiveness based on global market health.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MarketIntelligenceEngine()
        return cls._instance

    def __init__(self):
        self.indices = {
            "NIFTY": "^NSEI",
            "BANKNIFTY": "^NSEBANK",
            "VIX": "^INDIAVIX"
        }
        
    def evaluate_market(self, yf_provider) -> Dict:
        """
        Evaluates 12 steps of market health.
        Returns: Market Quality Score and Trading Mode.
        """
        score = 100
        reasons = []
        
        # Fetch Data
        nifty_df = yf_provider.fetch_ohlcv_yahoo(self.indices["NIFTY"], "1d", "5d")
        bank_df = yf_provider.fetch_ohlcv_yahoo(self.indices["BANKNIFTY"], "1d", "5d")
        vix_df = yf_provider.fetch_ohlcv_yahoo(self.indices["VIX"], "1d", "5d")
        
        if not nifty_df or len(nifty_df) < 2:
            return self._default_error_state("Missing NIFTY Data")
            
        nifty_latest = nifty_df[-1]
        nifty_prev = nifty_df[-2]
        
        # 1. Index Health
        nifty_change = (nifty_latest.close - nifty_prev.close) / nifty_prev.close
        nifty_trend = "Bullish" if nifty_change > 0 else "Bearish"
        
        bank_trend = "Neutral"
        if bank_df and len(bank_df) >= 2:
            bank_change = (bank_df[-1].close - bank_df[-2].close) / bank_df[-2].close
            bank_trend = "Bullish" if bank_change > 0 else "Bearish"
            
            # Divergence Check
            if nifty_trend != bank_trend:
                score -= 15
                reasons.append("Nifty/BankNifty Divergence")
                
        # 3. Volatility (VIX)
        vix_val = 15.0
        vix_status = "Normal"
        if vix_df and len(vix_df) > 0:
            vix_val = vix_df[-1].close
            if vix_val > 25:
                score -= 35
                vix_status = "Extreme"
                reasons.append("Extreme Volatility (VIX > 25)")
            elif vix_val > 20:
                score -= 20
                vix_status = "High"
                reasons.append("High Volatility (VIX > 20)")
            elif vix_val < 11:
                score -= 10
                vix_status = "Very Low"
                reasons.append("Low Volatility (Premium Decay)")
                
        # 5 & 6. Market Structure & Gap Analysis
        gap = (nifty_latest.open - nifty_prev.close) / nifty_prev.close
        if abs(gap) > 0.015:
            score -= 10
            reasons.append("Large Gap Open (Trap Risk)")
            
        # Overall Trend Strength
        if abs(nifty_change) < 0.002:
            score -= 15
            reasons.append("Sideways / Range Day")
            
        # Determine Mode
        score = max(0, min(100, score))
        
        if score >= 90:
            mode = "AGGRESSIVE"
            reason = "Very strong market conditions."
        elif score >= 80:
            mode = "NORMAL"
            reason = "Trade only the best setups."
        elif score >= 70:
            mode = "DEFENSIVE"
            reason = "Trade exceptional setups with reduced risk."
        else:
            mode = "NO TRADE"
            reason = "CAPITAL PROTECTION MODE ACTIVE"
            
        return {
            "mie_score": score,
            "mie_mode": mode,
            "mie_vix": round(vix_val, 2),
            "mie_vix_status": vix_status,
            "mie_nifty_trend": nifty_trend,
            "mie_reason": " | ".join(reasons) if reasons else reason
        }
        
    def _default_error_state(self, reason: str) -> Dict:
        return {
            "mie_score": 50,
            "mie_mode": "DEFENSIVE",
            "mie_vix": 0.0,
            "mie_vix_status": "Unknown",
            "mie_nifty_trend": "Unknown",
            "mie_reason": f"Data Error: {reason}"
        }
