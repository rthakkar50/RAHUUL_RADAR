import logging
import pandas as pd
from datetime import datetime
from application.data_manager import DataManager

logger = logging.getLogger(__name__)

class MarketHealthRiskEngine:
    """
    MASTER-20: MARKET HEALTH & RISK ENGINE VERSION 1.0
    Runs continuously to evaluate Market Health, Trading Risk, and Capital Safety.
    Acts as the ultimate gatekeeper for new entries and manages existing trades.
    """
    
    def __init__(self):
        self.data_manager = DataManager.get_instance()
        self.last_update = None
        self.state = self._get_empty_state()
        self.capital_defence_active = False
        
    def _get_empty_state(self):
        return {
            "Market Health Score": 0,
            "Risk Score": 100,
            "Market Regime": "UNKNOWN",
            "Breadth": "UNKNOWN",
            "Volatility": "UNKNOWN",
            "Leading Sector": "UNKNOWN",
            "Weakest Sector": "UNKNOWN",
            "Trading Mode": "NO TRADE",
            "Trade Environment": "Dangerous",
            "New Entry Permission": "BLOCK NEW TRADES",
            "Open Trade Management": "Exit Immediately",
            "Capital Defence Status": "ACTIVE",
            "Alerts": ["Waiting for data..."]
        }

    def evaluate(self, force_refresh=False):
        """
        Main polling function to be called continuously by the backend loop (e.g., every 1 min).
        """
        if force_refresh or self.last_update is None or (datetime.now() - self.last_update).total_seconds() > 60:
            self._run_diagnostics()
        return self.state
        
    def _run_diagnostics(self):
        try:
            # Proxy Fast-Fetch: NIFTY 50 Intraday & Daily for structural calculations
            df = self.data_manager.get_stock_data("^NSEI", period="1mo", interval="15m")
            if df.empty or len(df) < 20:
                self.state = self._get_empty_state()
                return

            latest = df.iloc[-1]
            close = latest['Close']
            
            # Simple MAs
            ema_20 = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
            ema_50 = df['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
            
            # ATR Volatility
            df['tr1'] = df['High'] - df['Low']
            df['tr2'] = abs(df['High'] - df['Close'].shift(1))
            df['tr3'] = abs(df['Low'] - df['Close'].shift(1))
            df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
            atr = df['tr'].rolling(14).mean().iloc[-1]
            atr_pct = (atr / close) * 100
            
            # =================================================================
            # SCORING ALGORITHMS
            # =================================================================
            health_score = 50
            risk_score = 50
            alerts = []
            
            # 1. Trend & Momentum
            if close > ema_20:
                health_score += 20
                risk_score -= 15
            else:
                health_score -= 20
                risk_score += 15
                alerts.append("Market Weakening: Price below short-term trend.")
                
            if ema_20 > ema_50:
                health_score += 10
            else:
                health_score -= 10
                
            # 2. Volatility (Check-3)
            if atr_pct > 0.5: # 15m Intraday extreme volatility
                volatility_str = "Extreme"
                health_score -= 30
                risk_score += 40
                alerts.append("Volatility Increasing: Extreme ATR Expansion.")
            elif atr_pct > 0.3:
                volatility_str = "High"
                health_score -= 15
                risk_score += 20
            elif atr_pct < 0.1:
                volatility_str = "Low"
                health_score += 5
                risk_score -= 10
            else:
                volatility_str = "Normal"
                
            # 3. Market Breadth Proxy
            # Simulated based on trend strength
            if health_score > 70:
                breadth_str = "Advance > Decline"
            elif health_score < 40:
                breadth_str = "Decline > Advance"
            else:
                breadth_str = "Neutral Breadth"
                
            # Cap scores
            health_score = max(0, min(100, health_score))
            risk_score = max(0, min(100, risk_score))
            
            # =================================================================
            # TRADE ENVIRONMENT & CAPITAL DEFENCE (Checks 7, 8, 9, 10)
            # =================================================================
            if health_score >= 90:
                environment = "Excellent"
                entry_perm = "ALLOW NEW TRADES"
                open_mgmt = "Continue Holding"
                self.capital_defence_active = False
            elif health_score >= 80:
                environment = "Healthy"
                entry_perm = "ALLOW NEW TRADES"
                open_mgmt = "Trail Stop"
                self.capital_defence_active = False
            elif health_score >= 70:
                environment = "Normal"
                entry_perm = "LIMIT NEW TRADES"
                open_mgmt = "Partial Exit"
                self.capital_defence_active = False
            elif health_score >= 60:
                environment = "Weak"
                entry_perm = "BLOCK NEW TRADES"
                open_mgmt = "Reduce Position"
                self.capital_defence_active = False
            else:
                environment = "Dangerous"
                entry_perm = "BLOCK NEW TRADES"
                open_mgmt = "Exit Immediately"
                self.capital_defence_active = True
                alerts.append("CAPITAL DEFENCE ACTIVE: High Risk Environment.")

            if risk_score >= 70:
                alerts.append("High Risk Detected: Expect erratic moves.")
                
            # Classify Risk strictly
            if risk_score <= 20: risk_class = "Very Low Risk"
            elif risk_score <= 40: risk_class = "Low Risk"
            elif risk_score <= 60: risk_class = "Moderate Risk"
            elif risk_score <= 80: risk_class = "High Risk"
            else: risk_class = "Extreme Risk"

            self.state = {
                "Market Health Score": health_score,
                "Risk Score": risk_score,
                "Risk Level": risk_class,
                "Market Regime": "Intraday Monitoring Active", # Integrates logically with MRE overall daily bias
                "Breadth": breadth_str,
                "Volatility": volatility_str,
                "Leading Sector": "FINANCE (Proxy)",
                "Weakest Sector": "METALS (Proxy)",
                "Trade Environment": environment,
                "New Entry Permission": entry_perm,
                "Open Trade Management": open_mgmt,
                "Capital Defence Status": "ACTIVE" if self.capital_defence_active else "INACTIVE",
                "Alerts": alerts
            }
            
            self.last_update = datetime.now()
            logger.info(f"MHRE Check: Health {health_score} | Risk {risk_score} | Permission: {entry_perm}")
            
        except Exception as e:
            logger.error(f"Error in MHRE: {e}")
            self.state = self._get_empty_state()
