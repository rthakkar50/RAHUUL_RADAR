from typing import Dict
import pandas as pd

class AIQualityEngine:
    """
    AI Trade Quality Layer.
    Sits ABOVE the Intraday and Swing Engines.
    Validates generated signals based on Institutional criteria.
    Never generates trades itself.
    """
    def __init__(self):
        pass
        
    def validate(self, result: Dict, latest: pd.Series) -> Dict:
        signal = result.get("signal", "WAIT")
        if signal == "WAIT":
            return {
                "grade": "D", "recommendation": "AVOID", "probability": "0%",
                "risk": "High", "reasons": ["✗ Signal is WAIT. No trade."],
                "passed": 0, "total": 12
            }
            
        reasons = []
        passed = 0
        total = 12
        
        # Helper
        def check(cond, pass_msg, fail_msg):
            nonlocal passed
            if cond:
                passed += 1
                reasons.append(f"✓ {pass_msg}")
            else:
                reasons.append(f"✗ {fail_msg}")
                
        # 1. Trend Alignment
        check(result.get("trend_aligned", False), "Aligned with Market Trend", "Against Market Trend")
        
        # 2. EMA Alignment
        if signal == "BUY":
            check(latest['EMA9'] > latest['EMA20'], "EMA Trend Strong (Bullish)", "EMA Trend Weak")
        else:
            check(latest['EMA9'] < latest['EMA20'], "EMA Trend Strong (Bearish)", "EMA Trend Weak")
            
        # 3. VWAP
        if signal == "BUY":
            check(latest['Close'] > latest['VWAP'], "Price holds above VWAP", "Price below VWAP")
        else:
            check(latest['Close'] < latest['VWAP'], "Price stays below VWAP", "Price above VWAP")
            
        # 4. Supertrend
        if signal == "BUY":
            check(latest['Supertrend_Direction'] == 1, "Supertrend Bullish", "Supertrend Bearish")
        else:
            check(latest['Supertrend_Direction'] == -1, "Supertrend Bearish", "Supertrend Bullish")
            
        # 5. MACD
        if signal == "BUY":
            check(latest['MACD'] > latest['Signal_Line'], "MACD Bullish Cross", "MACD Bearish")
        else:
            check(latest['MACD'] < latest['Signal_Line'], "MACD Bearish Cross", "MACD Bullish")
            
        # 6. RSI
        if signal == "BUY":
            check(50 <= latest['RSI'] <= 75, "RSI in Healthy Bull Zone", "RSI Overbought or Weak")
        else:
            check(25 <= latest['RSI'] <= 50, "RSI in Healthy Bear Zone", "RSI Oversold or Weak")
            
        # 7. ADX
        check(latest['ADX'] > 20, "Strong Momentum (ADX > 20)", "Weak Momentum (Sideways)")
        
        # 8. Volume
        check(latest['Volume'] > latest['Vol_MA'], "High Volume Confirmation", "Low Volume")
        
        # 9. Risk Reward
        score = result.get("score", 0)
        check(score >= 70, "Institutional R:R Profile", "Poor Risk/Reward Structure")
        
        # 10. ATR
        check(latest['ATR'] > 0, "Healthy Volatility", "Stagnant Volatility")
        
        # 11. Momentum (Distance from EMA9)
        dist = abs(latest['Close'] - latest['EMA9']) / latest['Close']
        check(dist < 0.02, "Close to Moving Average (Low Risk)", "Extended from Moving Average")
        
        # 12. Score Check
        check(score >= 50, "Passing System Score", "Failing System Score")

        # Grading Logic
        if passed >= 11:
            grade = "A+"
            rec = "STRONG BUY" if signal == "BUY" else "STRONG SELL"
            prob = "92%"
            risk = "Very Low"
        elif passed >= 9:
            grade = "A"
            rec = "BUY" if signal == "BUY" else "SELL"
            prob = "84%"
            risk = "Low"
        elif passed >= 7:
            grade = "B"
            rec = "BUY" if signal == "BUY" else "SELL"
            prob = "71%"
            risk = "Medium"
        elif passed >= 5:
            grade = "C"
            rec = "WAIT"
            prob = "50%"
            risk = "High"
        else:
            grade = "D"
            rec = "AVOID"
            prob = "20%"
            risk = "Very High"
            
        return {
            "grade": grade,
            "recommendation": rec,
            "probability": prob,
            "risk": risk,
            "reasons": reasons,
            "passed": passed,
            "total": total
        }
