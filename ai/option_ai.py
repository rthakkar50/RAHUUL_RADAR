import pandas as pd
import numpy as np

class OptionAI:
    def __init__(self):
        self.pcr_history = {}
        
    def analyze(self, df: pd.DataFrame, underlying_price: float, expiry: str, symbol: str):
        if df.empty or underlying_price == 0:
            return self._empty_response()
            
        total_ce_oi = df['CE_OI'].sum()
        total_pe_oi = df['PE_OI'].sum()
        pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0
        
        if symbol not in self.pcr_history:
            self.pcr_history[symbol] = []
        self.pcr_history[symbol].append(pcr)
        
        # 1. PCR Trend
        pcr_trend = "Stable"
        if len(self.pcr_history[symbol]) > 1:
            prev = self.pcr_history[symbol][-2]
            if pcr > prev + 0.05: pcr_trend = f"Rising (Bullish) | Prev: {prev}"
            elif pcr < prev - 0.05: pcr_trend = f"Falling (Bearish) | Prev: {prev}"
            else: pcr_trend = f"Stable | Prev: {prev}"
        
        # 2. Max Pain
        strikes = df['Strike'].tolist()
        max_pain = 0
        min_loss = float('inf')
        for strike in strikes:
            loss = 0
            for index, row in df.iterrows():
                if row['Strike'] < strike:
                    loss += row['PE_OI'] * (strike - row['Strike'])
                elif row['Strike'] > strike:
                    loss += row['CE_OI'] * (row['Strike'] - strike)
            if loss < min_loss:
                min_loss = loss
                max_pain = strike
                
        # 3. Support / Resistance (Highest OI)
        resistance = df.loc[df['CE_OI'].idxmax()]['Strike'] if not df['CE_OI'].empty else 0
        support = df.loc[df['PE_OI'].idxmax()]['Strike'] if not df['PE_OI'].empty else 0
        
        # 4. Smart Analysis (Build-up & Smart Money)
        nearest = df.iloc[(df['Strike'] - underlying_price).abs().argsort()[:5]]
        ce_chg_oi = nearest['CE_CHNG_OI'].sum()
        pe_chg_oi = nearest['PE_CHNG_OI'].sum()
        
        buildup = "Neutral"
        smart_money = ""
        unusual_activity = ""
        
        if ce_chg_oi > 0 and pe_chg_oi < 0:
            buildup = "Short Build-up (CE) / Long Unwinding (PE)"
        elif pe_chg_oi > 0 and ce_chg_oi < 0:
            buildup = "Long Build-up (PE) / Short Covering (CE)"
        elif ce_chg_oi > pe_chg_oi * 1.5:
            buildup = "Call Writing (Bearish)"
            if ce_chg_oi > 100000: smart_money = "🔥 Smart Money Selling"
        elif pe_chg_oi > ce_chg_oi * 1.5:
            buildup = "Put Writing (Bullish)"
            if pe_chg_oi > 100000: smart_money = "🔥 Smart Money Buying"
            
        # Unusual Activity Detect
        vol_spike = nearest['CE_Vol'].sum() + nearest['PE_Vol'].sum() > 2000000
        if vol_spike: unusual_activity += "⚡ Volume Spike "
        iv_spike = nearest['CE_IV'].mean() > 25 or nearest['PE_IV'].mean() > 25
        if iv_spike: unusual_activity += "⚡ IV Expansion "
            
        # 5. Confidence Engine 0-100
        conf = 50
        trend_bias = 0
        
        if pcr > 1.2: conf += 15; trend_bias += 1
        elif pcr < 0.8: conf += 15; trend_bias -= 1
        
        if underlying_price > max_pain: conf += 10; trend_bias += 1
        elif underlying_price < max_pain: conf += 10; trend_bias -= 1
        
        if underlying_price > vwap_proxy(underlying_price, max_pain): conf += 5; trend_bias += 1
        else: conf += 5; trend_bias -= 1
        
        if "Bullish" in buildup: conf += 15; trend_bias += 1
        elif "Bearish" in buildup: conf += 15; trend_bias -= 1
        
        if smart_money == "🔥 Smart Money Buying": conf += 10
        elif smart_money == "🔥 Smart Money Selling": conf += 10
        
        conf = min(max(conf, 0), 100) # Clamp 0-100
        
        # 6. Sentiment & Recommendation
        if trend_bias >= 2:
            sentiment = "Bullish"
        elif trend_bias <= -2:
            sentiment = "Bearish"
        else:
            sentiment = "Sideways"
            
        rec = "WAIT"
        reasons = []
        strategy = "No Trade"
        setup = None
        
        atm_strike = min(strikes, key=lambda x: abs(x - underlying_price))
        interval = abs(strikes[1] - strikes[0]) if len(strikes) > 1 else 100
        
        best_itm_ce = atm_strike - interval
        best_otm_ce = atm_strike + interval
        best_itm_pe = atm_strike + interval
        best_otm_pe = atm_strike - interval
        
        if sentiment == "Bullish" and conf >= 70:
            rec = "BUY ITM CE" if iv_spike else "BUY ATM CE"
            strategy = "BULL CALL SPREAD" if conf < 85 else "BUY ATM CE"
            reasons = [f"PCR Bullish ({pcr})", "Put Writing Detected", "Price > Max Pain"]
            
            ce_row = df[df['Strike'] == (best_itm_ce if iv_spike else atm_strike)]
            if not ce_row.empty:
                entry = ce_row.iloc[0]['CE_LTP']
                sl = max(0, entry * 0.7)
                setup = {
                    "strike": ce_row.iloc[0]['Strike'],
                    "entry": entry,
                    "sl": sl,
                    "target_1": entry * 1.3,
                    "target_2": entry * 1.6,
                    "time": "Intraday/BTST",
                    "premium_risk": "Moderate",
                    "rr": f"1:{round(((entry*1.6)-entry)/(entry-sl), 1) if entry > sl else 0}"
                }
                
        elif sentiment == "Bearish" and conf >= 70:
            rec = "BUY ITM PE" if iv_spike else "BUY ATM PE"
            strategy = "BEAR PUT SPREAD" if conf < 85 else "BUY ATM PE"
            reasons = [f"PCR Bearish ({pcr})", "Call Writing Detected", "Price < Max Pain"]
            
            pe_row = df[df['Strike'] == (best_itm_pe if iv_spike else atm_strike)]
            if not pe_row.empty:
                entry = pe_row.iloc[0]['PE_LTP']
                sl = max(0, entry * 0.7)
                setup = {
                    "strike": pe_row.iloc[0]['Strike'],
                    "entry": entry,
                    "sl": sl,
                    "target_1": entry * 1.3,
                    "target_2": entry * 1.6,
                    "time": "Intraday/BTST",
                    "premium_risk": "Moderate",
                    "rr": f"1:{round(((entry*1.6)-entry)/(entry-sl), 1) if entry > sl else 0}"
                }
        elif sentiment == "Sideways":
            rec = "IRON CONDOR"
            strategy = "IRON CONDOR"
            reasons = ["PCR Neutral", "OI Balanced", "Price hovering at Max Pain"]
            setup = {
                "strike": f"{best_otm_pe}PE / {best_otm_ce}CE",
                "entry": "Current Mkt",
                "sl": "Combined 30%",
                "target_1": "Combined 20% Decay",
                "target_2": "Expiry 0",
                "time": "Hold till Expiry",
                "premium_risk": "Low (Theta Decay)",
                "rr": "Variable"
            }
        else:
            rec = "WAIT"
            reasons = ["Conflicting Data", "Wait for clear trend"]
        
        return {
            "pcr": pcr,
            "pcr_trend": pcr_trend,
            "max_pain": max_pain,
            "support": support,
            "resistance": resistance,
            "buildup": buildup,
            "sentiment": sentiment,
            "confidence": conf,
            "recommendation": rec,
            "reasons": reasons,
            "strategy": strategy,
            "setup": setup,
            "smart_money": smart_money,
            "unusual_activity": unusual_activity,
            "best_atm": atm_strike,
            "best_itm_ce": best_itm_ce,
            "best_otm_ce": best_otm_ce,
            "best_itm_pe": best_itm_pe,
            "best_otm_pe": best_otm_pe
        }

    def _empty_response(self):
        return {
            "pcr": 0, "pcr_trend": "Stable", "max_pain": 0, "support": 0, "resistance": 0,
            "buildup": "N/A", "sentiment": "Neutral", "confidence": 0,
            "recommendation": "WAIT", "reasons": [], "strategy": "No Trade", "setup": None,
            "smart_money": "", "unusual_activity": "",
            "best_atm": 0, "best_itm_ce": 0, "best_otm_ce": 0, "best_itm_pe": 0, "best_otm_pe": 0
        }
        
def vwap_proxy(price, pain):
    return (price + pain) / 2
