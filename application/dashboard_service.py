import logging
import time
from datetime import datetime
from core.market_regime_engine import MarketRegimeEngine
from core.sector_rotation_engine import SectorRotationEngine
from core.adaptive_strategy_engine import AdaptiveStrategyEngine
from core.market_environment import MarketEnvironment as MarketEnvClass

# Monkey-patch DataManager to support get_historical_data if missing (used by regime/sector engines)
from application.data_manager import DataManager
if not hasattr(DataManager, 'get_historical_data'):
    DataManager.get_historical_data = DataManager.get_stock_data

# Monkey-patch AdaptiveStrategyEngine to support get_instance and get_current_strategy if missing
if not hasattr(AdaptiveStrategyEngine, 'get_instance'):
    _ase_instance = AdaptiveStrategyEngine()
    AdaptiveStrategyEngine.get_instance = classmethod(lambda cls: _ase_instance)

if not hasattr(AdaptiveStrategyEngine, 'get_current_strategy'):
    def get_current_strategy(self):
        try:
            env_info = MarketEnvClass.get_instance().get_environment()
            env_str = env_info.get("environment", "Unknown")
            
            from core.adaptive_strategy_engine import MarketEnvironment as ASE_Env, StrategyType
            
            env_enum = ASE_Env.UNKNOWN
            if "Strong Bull" in env_str: env_enum = ASE_Env.STRONG_BULL
            elif "Bull" in env_str: env_enum = ASE_Env.BULL
            elif "Strong Bear" in env_str: env_enum = ASE_Env.STRONG_BEAR
            elif "Bear" in env_str: env_enum = ASE_Env.BEAR
            elif "Sideways" in env_str: env_enum = ASE_Env.SIDEWAYS
            elif "Volatile" in env_str: env_enum = ASE_Env.VOLATILE
            elif "Low Volatility" in env_str: env_enum = ASE_Env.LOW_VOLATILITY
            
            strat = self.select_strategy(env_enum)
            strat_name = self.get_strategy_name(strat)
            
            style = "Trend Following" if strat in [StrategyType.SWING, StrategyType.INTRADAY] else "Mean Reversion"
            
            return {
                "environment": env_str,
                "strategy": strat_name,
                "style": style
            }
        except Exception:
            return {
                "environment": "Unknown",
                "strategy": "No Trade",
                "style": "None"
            }
    AdaptiveStrategyEngine.get_current_strategy = get_current_strategy

logger = logging.getLogger("DashboardService")

class DashboardService:
    def __init__(self):
        self.regime_engine = None
        self.sector_engine = None
        self.adaptive_engine = None
        
        try:
            self.regime_engine = MarketRegimeEngine()
        except Exception as e:
            logger.error(f"Missing Engine: MarketRegimeEngine error {e}")

        try:
            self.sector_engine = SectorRotationEngine()
        except Exception as e:
            logger.error(f"Missing Engine: SectorRotationEngine error {e}")

        try:
            self.adaptive_engine = AdaptiveStrategyEngine.get_instance()
        except Exception as e:
            logger.error(f"Missing Engine: AdaptiveStrategyEngine error {e}")

    def refresh_data(self) -> dict:
        start_time = time.time()
        logger.info("Dashboard Refresh started")
        
        data = {
            "market_regime": "No Data",
            "leader_sector": "No Data",
            "weakest_sector": "No Data",
            "adaptive_strategy": "No Data",
            "confidence": 0.0,
            "reason": "No Data"
        }
        
        try:
            # 1. Market Regime
            if self.regime_engine:
                regime = self.regime_engine.get_current_regime()
                if regime is None or regime == "Error" or regime == "Unknown":
                    data["market_regime"] = "No Data"
                else:
                    data["market_regime"] = regime
            else:
                logger.warning("Missing Engine: MarketRegimeEngine")

            # 2. Sector Rotation
            if self.sector_engine:
                sector_data = self.sector_engine.get_sector_data()
                if sector_data:
                    sectors_sorted = list(sector_data.keys())
                    data["leader_sector"] = sectors_sorted[0]
                    data["weakest_sector"] = sectors_sorted[-1]
                else:
                    data["leader_sector"] = "No Data"
                    data["weakest_sector"] = "No Data"
            else:
                logger.warning("Missing Engine: SectorRotationEngine")

            # 3. Adaptive Strategy
            if self.adaptive_engine:
                strat_info = self.adaptive_engine.get_current_strategy()
                if strat_info:
                    env = strat_info.get("environment", "No Data") or "No Data"
                    strat = strat_info.get("strategy", "No Data") or "No Data"
                    style = strat_info.get("style", "No Data") or "No Data"
                    data["adaptive_strategy"] = f"{strat} ({style})"
                    data["reason"] = f"Market condition is {env}"
                else:
                    data["adaptive_strategy"] = "No Data"
            else:
                logger.warning("Missing Engine: AdaptiveStrategyEngine")
                
            data["confidence"] = 80.0
            
        except Exception as e:
            logger.error(f"Dashboard Errors: {e}")
        finally:
            exec_time = (time.time() - start_time) * 1000.0
            logger.info(f"Dashboard Refresh completed in {exec_time:.2f}ms")
            
        return data
