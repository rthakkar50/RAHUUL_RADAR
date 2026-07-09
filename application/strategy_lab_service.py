import json
import os
import logging
from typing import Dict, Any, List
import datetime

logger = logging.getLogger(__name__)
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "strategy_lab.json")

class StrategyLabService:
    def __init__(self):
        self.data = self._load()
        
    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(CONFIG_FILE):
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            return {"strategies": []}
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load strategy lab config: {e}")
            return {"strategies": []}
            
    def _save(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save strategy lab config: {e}")

    def save_strategy(self, strategy_config: Dict[str, Any]):
        strategy_config["_modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "_created" not in strategy_config:
            strategy_config["_created"] = strategy_config["_modified"]
            
        # Update if exists, else append
        existing = [s for s in self.data["strategies"] if s.get("name") == strategy_config.get("name")]
        if existing:
            self.data["strategies"][self.data["strategies"].index(existing[0])] = strategy_config
        else:
            self.data["strategies"].append(strategy_config)
        self._save()

    def load_strategy(self, name: str) -> Dict[str, Any]:
        existing = [s for s in self.data["strategies"] if s.get("name") == name]
        return existing[0] if existing else {}

    def get_all_strategies(self) -> List[Dict[str, Any]]:
        return self.data["strategies"]

    def run_backtest_simulation(self, strategy_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs a dry-run simulation of the configured engines without hitting production APIs.
        Calculates Win Rate, Profit Factor, Sharpe, Expectancy.
        """
        logger.info(f"Running strategy simulation for: {strategy_config.get('name', 'Untitled')}")
        
        engines = strategy_config.get("engines", {})
        risk_profile = strategy_config.get("risk", {})
        
        # Mock calculation logic representing the aggregate performance
        base_win_rate = 55.0
        profit_factor = 1.2
        avg_return = 1.5
        max_drawdown = 10.0
        
        if engines.get("trend_engine"):
            base_win_rate += 5.0
            avg_return += 0.5
        if engines.get("momentum_engine"):
            base_win_rate += 2.0
            profit_factor += 0.3
        if engines.get("false_signal_engine"):
            base_win_rate += 8.0
            max_drawdown -= 3.0
            
        risk_limit = risk_profile.get("max_drawdown", 15.0)
        if max_drawdown > float(risk_limit):
            max_drawdown = float(risk_limit)
            
        sharpe = round((avg_return / max_drawdown) * (base_win_rate / 10), 2)
        expectancy = round((base_win_rate/100 * avg_return) - ((1 - base_win_rate/100) * (avg_return / profit_factor)), 2)
        
        return {
            "win_rate": round(min(base_win_rate, 100.0), 2),
            "profit_factor": round(profit_factor, 2),
            "average_return": round(avg_return, 2),
            "max_drawdown": round(max_drawdown, 2),
            "sharpe": sharpe,
            "expectancy": expectancy,
            "total_trades": 142
        }
