import numpy as np
import scipy.stats as si

class OptionGreeks:
    def __init__(self, risk_free_rate=0.07):
        self.r = risk_free_rate
        
    def calculate(self, S, K, T, v, option_type="CE"):
        """
        S: Current Price
        K: Strike Price
        T: Time to Expiry (in years)
        v: Implied Volatility (decimal)
        """
        if T <= 0.0 or v <= 0.0 or S <= 0.0 or K <= 0.0:
            return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}
            
        v = max(v, 0.0001)
        T = max(T, 0.0001)
        
        d1 = (np.log(S / K) + (self.r + 0.5 * v ** 2) * T) / (v * np.sqrt(T))
        d2 = (np.log(S / K) + (self.r - 0.5 * v ** 2) * T) / (v * np.sqrt(T))
        
        gamma = si.norm.pdf(d1) / (S * v * np.sqrt(T))
        vega = S * si.norm.pdf(d1) * np.sqrt(T) / 100
        
        if option_type == "CE":
            delta = si.norm.cdf(d1)
            theta = (- (S * v * si.norm.pdf(d1)) / (2 * np.sqrt(T)) - self.r * K * np.exp(-self.r * T) * si.norm.cdf(d2)) / 365
        else:
            delta = si.norm.cdf(d1) - 1
            theta = (- (S * v * si.norm.pdf(d1)) / (2 * np.sqrt(T)) + self.r * K * np.exp(-self.r * T) * si.norm.cdf(-d2)) / 365
            
        return {
            "delta": round(delta, 3), 
            "gamma": round(gamma, 4), 
            "theta": round(theta, 3), 
            "vega": round(vega, 3)
        }
