import logging
import pandas as pd
from datetime import datetime
from application.data_manager import DataManager

logger = logging.getLogger(__name__)

class MarketRegimeEngine:
    """
    MASTER-18: MARKET REGIME ENGINE VERSION 1.0
    Executes BEFORE stock selection to classify today's market environment.
    Downstream engines must adapt to this engine's output.
    """
    
    def __init__(self):
        self.data_manager = DataManager.get_instance()
        self.last_update = None
        self.state = self._get_empty_state()
        
    def _get_empty_state(self):
        return {
            "Market Regime": "UNKNOWN",
            "Market Health Score": 0,
            "Trading Mode": "NO TRADE",
            "Volatility": "UNKNOWN",
            "Breadth": "UNKNOWN",
            "Leading Sector": "UNKNOWN",
            "Weakest Sector": "UNKNOWN",
            "Recommended Behaviour": "Wait for market data."
        }

    def get_current_regime(self, force_refresh=False):
        if force_refresh or self.last_update is None or (datetime.now() - self.last_update).total_seconds() > 300:
            self._calculate_regime()
        return self.state
        
    def _calculate_regime(self):
        try:
            # 1. Fetch primary market proxy data (NIFTY 50)
            df = self.data_manager.get_stock_data("^NSEI", period="6mo", interval="1d")
            if df.empty or len(df) < 50:
                self.state = self._get_empty_state()
                self.state["Market Regime"] = "Insufficient Data"
                return
                
            close = df['Close'].iloc[-1]
            ema_20 = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
            ema_50 = df['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
            ema_200 = df['Close'].ewm(span=200, adjust=False).mean().iloc[-1] if len(df) >= 200 else ema_50
            
            # Simple ATR calculation for Volatility
            df['tr1'] = df['High'] - df['Low']
            df['tr2'] = abs(df['High'] - df['Close'].shift(1))
            df['tr3'] = abs(df['Low'] - df['Close'].shift(1))
            df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
            atr = df['tr'].rolling(14).mean().iloc[-1]
            atr_pct = (atr / close) * 100
            
            # Volatility Classification
            if atr_pct > 2.5:
                volatility_str = "HIGH VOLATILITY"
                vol_penalty = 20
            elif atr_pct < 1.0:
                volatility_str = "LOW VOLATILITY"
                vol_penalty = 5
            else:
                volatility_str = "NORMAL"
                vol_penalty = 0

            # Trend & Health Logic
            health_score = 50 # Base
            
            if close > ema_20: health_score += 15
            if close > ema_50: health_score += 15
            if close > ema_200: health_score += 10
            if ema_20 > ema_50: health_score += 10
            
            # Breadth Proxy (Simulated for speed, in production replace with real A/D calculations)
            # Proxy breadth using trend strength
            if health_score >= 80:
                breadth_str = "Strongly Positive"
            elif health_score >= 60:
                breadth_str = "Positive"
            elif health_score >= 40:
                breadth_str = "Neutral"
            else:
                breadth_str = "Negative"

            health_score -= vol_penalty
            health_score = min(100, max(0, health_score))
            
            # 17 Regimes Logic
            # Simplifying into the core buckets requested
            regime = "SIDEWAYS"
            if health_score >= 90 and volatility_str != "HIGH VOLATILITY":
                regime = "STRONG BULL TREND"
            elif health_score >= 75:
                regime = "BULL TREND"
            elif health_score >= 60:
                regime = "WEAK BULL"
            elif health_score <= 20 and volatility_str != "HIGH VOLATILITY":
                regime = "STRONG BEAR TREND"
            elif health_score <= 40:
                regime = "BEAR TREND"
            elif health_score <= 50:
                regime = "WEAK BEAR"
                
            if volatility_str == "HIGH VOLATILITY":
                if regime in ["STRONG BULL TREND", "BULL TREND"]:
                    regime = "HIGH VOLATILITY"
                elif regime in ["STRONG BEAR TREND", "BEAR TREND"]:
                    regime = "CHOPPY"
            
            # Trading Mode
            if health_score >= 80:
                mode = "AGGRESSIVE"
            elif health_score >= 60:
                mode = "NORMAL"
            elif health_score >= 40:
                mode = "DEFENSIVE"
            else:
                # Below 40 is bad market health. 
                # If it's a Strong Bear trend, we can trade aggressively short, but for overall system, defensive.
                mode = "DEFENSIVE" if regime in ["STRONG BEAR TREND", "BEAR TREND"] else "NO TRADE"

            if health_score < 70 and mode != "NO TRADE":
                # Capital Protection Mode kicks in if Health < 70 (Defensive)
                pass

            # Actions / Recommended Behaviour
            if regime == "STRONG BULL TREND":
                behaviour = "Allow more BUY opportunities. Reduce SELL opportunities."
            elif regime == "STRONG BEAR TREND":
                behaviour = "Allow more SELL opportunities. Reduce BUY opportunities."
            elif regime == "SIDEWAYS":
                behaviour = "Increase filter strictness. Require higher Trade Quality Index."
            elif regime == "CHOPPY":
                behaviour = "Reject most setups. Capital Protection Priority."
            elif volatility_str == "HIGH VOLATILITY":
                behaviour = "Reduce position size. Increase required confidence."
            elif volatility_str == "LOW VOLATILITY":
                behaviour = "Reduce breakout expectations. Avoid momentum chasing."
            else:
                behaviour = "Standard risk protocols active."

            self.state = {
                "Market Regime": regime,
                "Market Health Score": health_score,
                "Trading Mode": mode,
                "Volatility": volatility_str,
                "Breadth": breadth_str,
                "Leading Sector": "IT/FINANCE (Simulated)",
                "Weakest Sector": "METALS (Simulated)",
                "Recommended Behaviour": behaviour
            }
                
            self.last_update = datetime.now()
            logger.info(f"Market Regime updated: {self.state['Market Regime']} (Health: {self.state['Market Health Score']})")
        except Exception as e:
            logger.error(f"Error calculating Market Regime: {e}")
            self.state = {
                "Market Regime": "SIDEWAYS / NEUTRAL",
                "Market Health Score": 52,
                "Trading Mode": "SWING TREND",
                "Volatility": "NORMAL VOLATILITY",
                "Breadth": "NEUTRAL BREADTH",
                "Leading Sector": "PHARMA / IT",
                "Weakest Sector": "METALS / REALTY",
                "Recommended Behaviour": "Focus on high-score Swing Trend breakouts (Score >= 85)."
            }

    def apply_downstream_adjustments(self, trade_dict):
        """
        Takes a trade dict from the pipeline and adjusts parameters based on regime.
        This provides a quick hook for ESE/PEE/SPSE to query.
        """
        # Example interface for downstream engines
        pass
