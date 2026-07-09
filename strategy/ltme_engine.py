from typing import Dict
import pandas as pd
from strategy.eme_engine import ExitManagementEngine

class LiveTradeMonitoringEngine:
    """
    LIVE TRADE MONITORING ENGINE (LTME) V2.0
    Master health monitor for active trades. Wraps EME.
    """
    def __init__(self):
        self.eme = ExitManagementEngine()

    def monitor_trade(self, position: Dict, df: pd.DataFrame, market_trend: str, sector_trend: str) -> Dict:
        """
        Monitors trade health on every refresh cycle.
        Returns full health report and updated EME stats.
        """
        # 1. Run Core EME (Trailing SL, Stop Loss Hit, Time Exit)
        eme_res = self.eme.evaluate_exit(position, df)
        
        health_score = 100
        alerts = []
        
        if df.empty:
            return {
                "ltme_health": 0, "ltme_status": "WAIT", "ltme_alerts": "No Data",
                **eme_res
            }
            
        latest = df.iloc[-1]
        signal = position.get("signal", "BUY")
        current_price = latest['Close']
        
        # Check 1 & 2: Market & Sector Health
        market_health = "Strong"
        if signal == "BUY" and market_trend == "DOWNTREND":
            health_score -= 10
            alerts.append("Market Divergence")
            market_health = "Weak"
        elif signal == "SELL" and market_trend == "UPTREND":
            health_score -= 10
            alerts.append("Market Divergence")
            market_health = "Weak"
            
        sector_health = "Strong"
        if signal == "BUY" and sector_trend == "DOWNTREND":
            health_score -= 10
            alerts.append("Sector Weakening")
            sector_health = "Weak"
        elif signal == "SELL" and sector_trend == "UPTREND":
            health_score -= 10
            alerts.append("Sector Weakening")
            sector_health = "Weak"

        # Check 4: Volume
        vol_ma = df['Volume'].rolling(20).mean().iloc[-1]
        if latest['Volume'] < (vol_ma * 0.5):
            health_score -= 10
            alerts.append("Volume Drying")
            
        # Check 6: VWAP
        df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = (df['TP'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        vwap = df.iloc[-1]['VWAP']
        
        if signal == "BUY" and current_price < vwap:
            health_score -= 15
            alerts.append("VWAP Lost")
        elif signal == "SELL" and current_price > vwap:
            health_score -= 15
            alerts.append("VWAP Lost")
            
        # Determine LTME Status
        health_score = max(0, min(100, health_score))
        
        # Override with EME hard exits if they trigger
        eme_status = eme_res["status"]
        if eme_status in ["FULL EXIT", "EMERGENCY EXIT"]:
            ltme_status = eme_status
            health_score = 0
            alerts.append(eme_res["reason"])
        elif eme_status == "PARTIAL EXIT":
            ltme_status = "BOOK PARTIAL"
            alerts.append(eme_res["reason"])
        elif eme_status == "TRAIL SL":
            ltme_status = "MOVE SL"
            alerts.append(eme_res["reason"])
        else: # EME is HOLD, evaluate LTME health
            if health_score >= 90:
                ltme_status = "HOLD"
            elif health_score >= 80:
                ltme_status = "HOLD WITH CAUTION"
            else:
                ltme_status = "EXIT RECOMMENDED" if health_score >= 70 else "EMERGENCY EXIT"
                
        # Base confidence calculation based on health
        base_confidence = position.get("confidence", "85%")
        if isinstance(base_confidence, str):
            try:
                conf = int(base_confidence.replace("%", ""))
            except:
                conf = 85
        else:
            conf = int(base_confidence)
            
        adjusted_conf = min(conf, health_score) if health_score < 90 else conf

        return {
            "ltme_health": health_score,
            "ltme_status": ltme_status,
            "ltme_alerts": " | ".join(alerts) if alerts else "Trade Healthy",
            "ltme_market": market_health,
            "ltme_sector": sector_health,
            "ltme_conf": f"{adjusted_conf}%",
            **eme_res
        }
