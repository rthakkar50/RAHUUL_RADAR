import yfinance as yf
from dataclasses import dataclass
from typing import Optional, List, Dict
from scipy.stats import norm
import numpy as np

@dataclass
class OptionMetrics:
    symbol: str
    pcr: float
    max_pain: float
    iv_percentile: float
    call_writing_strike: float
    put_writing_strike: float
    oi_bias: str

class OptionsEngine:
    """
    Dedicated engine for deep Option Chain analytics.
    """
    @staticmethod
    def _black_scholes_greeks(S, K, T, r, sigma, option_type="call"):
        """
        Approximates Delta and Gamma using basic Black Scholes parameters.
        S = Spot price
        K = Strike price
        T = Time to expiration (in years)
        r = Risk-free rate
        sigma = Implied volatility
        """
        if T <= 0 or sigma <= 0:
            return 0.0, 0.0
            
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        delta = norm.cdf(d1) if option_type == "call" else norm.cdf(d1) - 1
        
        return delta, gamma

    def analyze_chain(self, symbol: str) -> Optional[OptionMetrics]:
        try:
            ticker = yf.Ticker(symbol)
            exp_dates = ticker.options
            if not exp_dates:
                return None
                
            chain = ticker.option_chain(exp_dates[0])
            calls = chain.calls
            puts = chain.puts
            
            total_call_oi = calls["openInterest"].sum()
            total_put_oi = puts["openInterest"].sum()
            
            pcr = round(total_put_oi / total_call_oi, 3) if total_call_oi > 0 else 0.0
            
            # Max Pain
            strikes = sorted(list(set(calls["strike"]).union(set(puts["strike"]))))
            max_pain = 0
            min_loss = float('inf')
            
            for strike in strikes:
                loss = 0
                for _, row in calls.dropna(subset=['strike', 'openInterest']).iterrows():
                    if row['strike'] < strike:
                        loss += (strike - row['strike']) * row['openInterest']
                for _, row in puts.dropna(subset=['strike', 'openInterest']).iterrows():
                    if row['strike'] > strike:
                        loss += (row['strike'] - strike) * row['openInterest']
                        
                if loss < min_loss:
                    min_loss = loss
                    max_pain = strike
                    
            # Identify Writing Zones (Highest OI)
            call_writing_strike = calls.loc[calls["openInterest"].idxmax()]["strike"] if not calls.empty else 0
            put_writing_strike = puts.loc[puts["openInterest"].idxmax()]["strike"] if not puts.empty else 0
            
            # Simple Bias
            oi_bias = "NEUTRAL"
            if pcr < 0.7: oi_bias = "BULLISH"
            elif pcr > 1.3: oi_bias = "BEARISH"
            
            return OptionMetrics(
                symbol=symbol,
                pcr=pcr,
                max_pain=max_pain,
                iv_percentile=50.0, # Placeholder until historical IV is loaded
                call_writing_strike=call_writing_strike,
                put_writing_strike=put_writing_strike,
                oi_bias=oi_bias
            )
            
        except Exception:
            return None
