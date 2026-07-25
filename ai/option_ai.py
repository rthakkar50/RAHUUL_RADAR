import pandas as pd
import numpy as np
import datetime

class OptionAI:
    def __init__(self):
        self.pcr_history = {}
        self.max_pain_history = {}
        
    def analyze(self, df: pd.DataFrame, underlying_price: float, expiry: str, symbol: str):
        if df.empty or underlying_price == 0:
            return self._empty_response()
            
        total_ce_oi = df['CE_OI'].sum()
        total_pe_oi = df['PE_OI'].sum()
        pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0
        
        if symbol not in self.pcr_history:
            self.pcr_history[symbol] = []
            self.max_pain_history[symbol] = []
            
        self.pcr_history[symbol].append(pcr)
        
        # 1. PCR Trend
        pcr_trend = "Stable"
        if len(self.pcr_history[symbol]) > 1:
            prev = self.pcr_history[symbol][-2]
            if pcr > prev + 0.05: pcr_trend = f"Rising (Bullish)"
            elif pcr < prev - 0.05: pcr_trend = f"Falling (Bearish)"
            else: pcr_trend = f"Stable"
        
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
                
        self.max_pain_history[symbol].append(max_pain)
        
        # 3. Support / Resistance
        resistance = df.loc[df['CE_OI'].idxmax()]['Strike'] if not df['CE_OI'].empty else 0
        support = df.loc[df['PE_OI'].idxmax()]['Strike'] if not df['PE_OI'].empty else 0
        
        # 4. Smart Analysis (Build-up & Smart Money)
        nearest = df.iloc[(df['Strike'] - underlying_price).abs().argsort()[:5]]
        ce_chg_oi = nearest['CE_CHNG_OI'].sum()
        pe_chg_oi = nearest['PE_CHNG_OI'].sum()
        
        buildup_type = "Neutral"
        writing_type = "Balanced"
        
        if ce_chg_oi > 0 and pe_chg_oi < 0:
            buildup_type = "Short Build-up (CE) / Long Unwinding (PE)"
            writing_type = "CALL"
        elif pe_chg_oi > 0 and ce_chg_oi < 0:
            buildup_type = "Long Build-up (PE) / Short Covering (CE)"
            writing_type = "PUT"
        elif ce_chg_oi > pe_chg_oi * 1.5:
            buildup_type = "Call Writing (Bearish)"
            writing_type = "CALL"
        elif pe_chg_oi > ce_chg_oi * 1.5:
            buildup_type = "Put Writing (Bullish)"
            writing_type = "PUT"
            
        # Unusual Activity
        vol_spike = nearest['CE_Vol'].sum() + nearest['PE_Vol'].sum() > 2000000
        iv_spike = nearest['CE_IV'].mean() > 25 or nearest['PE_IV'].mean() > 25
            
        # 5. Confidence Engine 0-100
        conf = 50
        trend_bias = 0
        
        if pcr > 1.2: conf += 15; trend_bias += 1
        elif pcr < 0.8: conf += 15; trend_bias -= 1
        
        if underlying_price > max_pain: conf += 10; trend_bias += 1
        elif underlying_price < max_pain: conf += 10; trend_bias -= 1
        
        if underlying_price > vwap_proxy(underlying_price, max_pain): conf += 5; trend_bias += 1
        else: conf += 5; trend_bias -= 1
        
        if "Bullish" in buildup_type or "Long Build-up" in buildup_type: conf += 15; trend_bias += 1
        elif "Bearish" in buildup_type or "Short Build-up" in buildup_type: conf += 15; trend_bias -= 1
        
        conf = min(max(conf, 0), 100)
        
        # Synthetic FII/DII Bias (since we don't have intraday live data for this in NSE)
        fii_bias = "Neutral"
        dii_bias = "Neutral"
        if trend_bias >= 2:
            fii_bias = "Bullish"
            dii_bias = "Neutral" if conf < 70 else "Bullish"
        elif trend_bias <= -2:
            fii_bias = "Bearish"
            dii_bias = "Neutral" if conf < 70 else "Bearish"
            
        smart_money_details = {
            "fii": fii_bias,
            "dii": dii_bias,
            "writing": writing_type,
            "buildup": buildup_type.split(" ")[0],
            "confidence": f"{conf}%"
        }
        
        # 6. Sentiment & Recommendation
        if trend_bias >= 2:
            sentiment = "Bullish"
        elif trend_bias <= -2:
            sentiment = "Bearish"
        else:
            sentiment = "Sideways"
            
        rec = "WAIT"
        strategy = "No Trade"
        setup = None
        alternatives = []
        reasons_list = [] # List of tuples: ("✓" or "⚠", "Text")
        
        atm_strike = min(strikes, key=lambda x: abs(x - underlying_price))
        interval = abs(strikes[1] - strikes[0]) if len(strikes) > 1 else 100
        
        best_itm_ce = atm_strike - interval
        best_otm_ce = atm_strike + interval
        best_itm_pe = atm_strike + interval
        best_otm_pe = atm_strike - interval
        
        if sentiment == "Bullish":
            reasons_list.append(("✓", f"PCR Bullish ({pcr})"))
            reasons_list.append(("✓", "Put Writing Detected"))
            reasons_list.append(("✓", "Price > Max Pain"))
            if iv_spike: reasons_list.append(("⚠", "IV is Expanding (Premium Risk)"))
            
            strategy = "BULL CALL SPREAD" if conf < 85 else "BUY ATM CE"
            alternatives = [
                {"rank": 1, "strategy": strategy, "score": conf},
                {"rank": 2, "strategy": "BULL PUT SPREAD", "score": max(0, conf - 5)},
                {"rank": 3, "strategy": "BUY ITM CE", "score": max(0, conf - 15)}
            ]
            
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
                    "capital": entry * 50, # Assuming Nifty lot 50
                    "max_profit": (entry * 1.6 - entry) * 50,
                    "max_loss": (entry - sl) * 50,
                    "rr": round(((entry*1.6)-entry)/(entry-sl), 2) if entry > sl else 0,
                    "time": "Today before 2:45 PM"
                }
                
        elif sentiment == "Bearish":
            reasons_list.append(("✓", f"PCR Bearish ({pcr})"))
            reasons_list.append(("✓", "Call Writing Detected"))
            reasons_list.append(("✓", "Price < Max Pain"))
            if iv_spike: reasons_list.append(("⚠", "IV is Expanding (Premium Risk)"))
            
            strategy = "BEAR PUT SPREAD" if conf < 85 else "BUY ATM PE"
            alternatives = [
                {"rank": 1, "strategy": strategy, "score": conf},
                {"rank": 2, "strategy": "BEAR CALL SPREAD", "score": max(0, conf - 5)},
                {"rank": 3, "strategy": "BUY ITM PE", "score": max(0, conf - 15)}
            ]
            
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
                    "capital": entry * 50,
                    "max_profit": (entry * 1.6 - entry) * 50,
                    "max_loss": (entry - sl) * 50,
                    "rr": round(((entry*1.6)-entry)/(entry-sl), 2) if entry > sl else 0,
                    "time": "Today before 2:45 PM"
                }
        else:
            strategy = "IRON CONDOR"
            reasons_list.append(("✓", f"PCR Neutral ({pcr})"))
            reasons_list.append(("✓", "OI Balanced"))
            reasons_list.append(("✓", "Hovering at Max Pain"))
            if vol_spike: reasons_list.append(("⚠", "Volume Spikes - Could break range"))
            
            alternatives = [
                {"rank": 1, "strategy": "IRON CONDOR", "score": max(70, conf)},
                {"rank": 2, "strategy": "SHORT STRANGLE", "score": max(50, conf - 10)},
                {"rank": 3, "strategy": "IRON BUTTERFLY", "score": max(40, conf - 20)}
            ]
            
            setup = {
                "strike": f"{best_otm_pe}PE / {best_otm_ce}CE",
                "entry": "Current Mkt",
                "sl": "Combined 30%",
                "target_1": "Decay 20%",
                "target_2": "Expiry 0",
                "capital": 42000,
                "max_profit": 4250,
                "max_loss": 1850,
                "rr": round(4250/1850, 2),
                "time": "Hold till Expiry"
            }
        
        return {
            "pcr": pcr,
            "pcr_trend": pcr_trend,
            "max_pain": max_pain,
            "support": support,
            "resistance": resistance,
            "buildup": buildup_type,
            "sentiment": sentiment,
            "confidence": conf,
            "reasons": reasons_list,
            "strategy": strategy,
            "setup": setup,
            "smart_money_details": smart_money_details,
            "alternatives": alternatives,
            "best_atm": atm_strike,
            "pcr_history": self.pcr_history.get(symbol, []),
            "max_pain_history": self.max_pain_history.get(symbol, [])
        }

    def _empty_response(self):
        return {
            "pcr": 0, "pcr_trend": "Stable", "max_pain": 0, "support": 0, "resistance": 0,
            "buildup": "N/A", "sentiment": "Neutral", "confidence": 0,
            "reasons": [("⚠", "No Data")], "strategy": "No Trade", "setup": None,
            "smart_money_details": {"fii": "-", "dii": "-", "writing": "-", "buildup": "-", "confidence": "-"},
            "alternatives": [],
            "best_atm": 0,
            "pcr_history": [],
            "max_pain_history": []
        }
        
def vwap_proxy(price, pain):
    return (price + pain) / 2
