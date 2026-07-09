from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime

class ExitManagementEngine:
    """
    EXIT MANAGEMENT ENGINE (EME) V2.0
    Only responsibility: "WHEN TO EXIT"
    Protects profit, prevents late exits.
    """
    def __init__(self):
        pass

    def evaluate_exit(self, position: Dict, df: pd.DataFrame) -> Dict:
        """
        Evaluate if an open position should be exited or trailed.
        Returns:
            status: HOLD, TRAIL SL, PARTIAL EXIT, FULL EXIT, EMERGENCY EXIT
            score: 0-100
            reason: str
            warning: str
            new_sl: float
            profit: float
            risk: float
        """
        if df.empty:
            return {"status": "HOLD", "score": 95, "reason": "No Data", "warning": "", "new_sl": position.get("sl", 0)}

        latest = df.iloc[-1]
        
        entry_price = float(position.get("entry_price", 0))
        qty = float(position.get("qty", 0))
        current_sl = float(position.get("sl", 0))
        signal = position.get("signal", "BUY")
        tp1 = float(position.get("target_1", 0))
        tp2 = float(position.get("target_2", 0))
        
        current_price = latest['Close']
        new_sl = current_sl
        
        if signal == "BUY":
            profit = (current_price - entry_price) * qty
            risk = (entry_price - current_sl) * qty
        else:
            profit = (entry_price - current_price) * qty
            risk = (current_sl - entry_price) * qty
            
        score = 100
        reason = "Trend is intact"
        warning = ""
        status = "HOLD"
        
        # 1. TIME EXIT (3:15 PM)
        now = datetime.now()
        if now.hour == 15 and now.minute >= 15:
            return {
                "status": "FULL EXIT", "score": 60, "reason": "EXIT BEFORE MARKET CLOSE",
                "warning": "Time Exit", "new_sl": new_sl, "profit": profit, "risk": risk
            }

        # 2. TRAILING SL & PARTIAL PROFIT
        if signal == "BUY":
            if current_price >= tp1 and current_sl < entry_price:
                new_sl = entry_price
                status = "PARTIAL EXIT"
                score = 85
                reason = "Hit Target-1. Book 50%. Move SL to Cost."
            elif current_price >= tp2:
                # Trail below donchian or structure (simplification: trail close)
                trail_level = df['Low'].rolling(5).min().iloc[-1]
                if trail_level > new_sl:
                    new_sl = trail_level
                status = "TRAIL SL"
                score = 92
                reason = "Hit Target-2. Trailing SL below structure."
        else: # SELL
            if current_price <= tp1 and current_sl > entry_price:
                new_sl = entry_price
                status = "PARTIAL EXIT"
                score = 85
                reason = "Hit Target-1. Book 50%. Move SL to Cost."
            elif current_price <= tp2:
                trail_level = df['High'].rolling(5).max().iloc[-1]
                if trail_level < new_sl:
                    new_sl = trail_level
                status = "TRAIL SL"
                score = 92
                reason = "Hit Target-2. Trailing SL above structure."

        # 3. EMERGENCY EXIT / STOP LOSS HIT
        if signal == "BUY" and current_price <= new_sl:
            status = "EMERGENCY EXIT" if current_price < (new_sl * 0.995) else "FULL EXIT"
            score = 65
            reason = "Stop Loss Hit"
            
        elif signal == "SELL" and current_price >= new_sl:
            status = "EMERGENCY EXIT" if current_price > (new_sl * 1.005) else "FULL EXIT"
            score = 65
            reason = "Stop Loss Hit"
            
        # 4. MOMENTUM / EMERGENCY CONDITIONS
        if status not in ["FULL EXIT", "EMERGENCY EXIT"]:
            # Check VWAP (approx calculation for emergency)
            df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
            df['VWAP'] = (df['TP'] * df['Volume']).cumsum() / df['Volume'].cumsum()
            vwap = df.iloc[-1]['VWAP']
            vol_ma = df['Volume'].rolling(20).mean().iloc[-1]
            
            if signal == "BUY" and current_price < vwap:
                score -= 15
                warning = "VWAP Lost"
            elif signal == "SELL" and current_price > vwap:
                score -= 15
                warning = "VWAP Lost"
                
            if latest['Volume'] < (vol_ma * 0.5):
                score -= 10
                warning = "Volume Disappearing" if not warning else warning + " | Vol Drop"
                
            if score < 70:
                status = "EMERGENCY EXIT"
                reason = "Momentum / Market Reversed"
            elif score < 80 and status == "HOLD":
                status = "FULL EXIT"
                reason = "Setup degrading"
                
        return {
            "status": status,
            "score": max(0, min(100, score)),
            "reason": reason,
            "warning": warning,
            "new_sl": round(new_sl, 2),
            "profit": round(profit, 2),
            "risk": round(risk, 2)
        }
