from enum import Enum
from typing import Any, Union, Dict, Tuple
from dataclasses import dataclass
import os
import logging
from datetime import datetime

class MarketEnvironment(Enum):
    """Enum representing the detected market regimes/environments."""
    UNKNOWN = 0
    BULL = 1
    STRONG_BULL = 2
    BEAR = 3
    STRONG_BEAR = 4
    SIDEWAYS = 5
    VOLATILE = 6
    LOW_VOLATILITY = 7

class StrategyType(Enum):
    """Enum representing the trading strategy types."""
    SWING = 0
    INTRADAY = 1
    SCALPING = 2
    OPTION_SCALPING = 3
    NO_TRADE = 4

@dataclass
class MarketSnapshot:
    """Dataclass acting as a container for current market indicators."""
    trend_direction: str
    adx: float
    atr: float
    rsi: float
    price_above_vwap: bool
    volume_ratio: float
    market_breadth: float
    sector_strength: float
    relative_strength: float
    option_chain_bias: str

class AdaptiveStrategyEngine:
    """
    Engine to dynamically detect the market environment and select 
    the most appropriate trading strategy.
    """

    def __init__(self) -> None:
        """Initializes the AdaptiveStrategyEngine instance and configures logger."""
        self.log_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs"))
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file: str = os.path.join(self.log_dir, "adaptive_strategy.log")
        
        # Touch log file to ensure it exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                pass
                
        self.logger = logging.getLogger("AdaptiveStrategy")
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers to avoid duplicates and close them
        if self.logger.hasHandlers():
            for h in list(self.logger.handlers):
                h.close()
            self.logger.handlers.clear()
            
        handler = logging.FileHandler(self.log_file)
        # Formatter format maps to: Timestamp - Message
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_strategy_decision(self, environment: MarketEnvironment, strategy_type: StrategyType) -> None:
        """
        Logs the market environment and selected strategy to adaptive_strategy.log.

        Args:
            environment: The classified MarketEnvironment.
            strategy_type: The selected StrategyType.
        """
        env_name: str = environment.name
        strat_name: str = self.get_strategy_name(strategy_type)
        self.logger.info(f"Market Environment: {env_name} | Selected Strategy: {strat_name}")

    def detect_market_environment(self, snapshot: Union[Dict[str, Any], MarketSnapshot, Any]) -> MarketEnvironment:
        """
        Detects the current market environment from the given market snapshot.

        Args:
            snapshot: A dictionary, MarketSnapshot object, or custom mock object containing market parameters.

        Returns:
            MarketEnvironment: The classified market environment.
        """
        if not snapshot:
            return MarketEnvironment.UNKNOWN

        # Helper to retrieve properties from either object attributes or dict keys
        def get_val(key: str, default: Any = None) -> Any:
            if isinstance(snapshot, dict):
                return snapshot.get(key, default)
            return getattr(snapshot, key, default)

        adx: float = float(get_val("adx", 0.0))
        atr: float = float(get_val("atr", 0.0))
        price_above_vwap: bool = bool(get_val("price_above_vwap", False))
        
        # Read either trend_direction (from MarketSnapshot) or trend (from dict/legacy mock)
        trend_raw: Any = get_val("trend_direction", get_val("trend", ""))
        trend: str = str(trend_raw).upper() if trend_raw else ""
        
        # Determine ATR states
        atr_extremely_low: bool = bool(get_val("atr_extremely_low", False))
        if not atr_extremely_low and isinstance(atr, (int, float)) and 0 < atr < 0.5:
            atr_extremely_low = True
            
        atr_high: bool = bool(get_val("atr_high", False))
        if not atr_high and isinstance(atr, (int, float)) and atr > 2.0:
            atr_high = True

        # Rule 5: IF ATR is extremely low -> LOW_VOLATILITY
        if atr_extremely_low:
            return MarketEnvironment.LOW_VOLATILITY

        # Rule 6: IF ATR is high AND ADX < 20 -> VOLATILE
        if atr_high and adx < 20:
            return MarketEnvironment.VOLATILE

        if trend == "BULL":
            # Rule 1: IF ADX >= 30 AND Trend == BULL AND Price Above VWAP -> STRONG_BULL
            if adx >= 30 and price_above_vwap:
                return MarketEnvironment.STRONG_BULL
            # Rule 2: IF ADX >= 20 AND Trend == BULL -> BULL
            elif adx >= 20:
                return MarketEnvironment.BULL

        elif trend == "BEAR":
            # Rule 3: IF ADX >= 30 AND Trend == BEAR -> STRONG_BEAR
            if adx >= 30:
                return MarketEnvironment.STRONG_BEAR
            # Rule 4: IF ADX >= 20 AND Trend == BEAR -> BEAR
            elif adx >= 20:
                return MarketEnvironment.BEAR

        # Default
        return MarketEnvironment.SIDEWAYS

    def select_strategy(self, environment: MarketEnvironment) -> StrategyType:
        """
        Maps the detected MarketEnvironment to the optimal StrategyType.

        Args:
            environment: The classified MarketEnvironment.

        Returns:
            StrategyType: The selected strategy type.
        """
        match environment:
            case MarketEnvironment.STRONG_BULL:
                return StrategyType.INTRADAY
            case MarketEnvironment.BULL:
                return StrategyType.SWING
            case MarketEnvironment.STRONG_BEAR:
                return StrategyType.INTRADAY
            case MarketEnvironment.BEAR:
                return StrategyType.SWING
            case MarketEnvironment.VOLATILE:
                return StrategyType.SCALPING
            case MarketEnvironment.LOW_VOLATILITY:
                return StrategyType.NO_TRADE
            case MarketEnvironment.SIDEWAYS:
                return StrategyType.NO_TRADE
            case _:
                return StrategyType.NO_TRADE

    def get_strategy_name(self, strategy_type: StrategyType) -> str:
        """
        Maps a StrategyType enum value to its human-readable display name.

        Args:
            strategy_type: The StrategyType to name.

        Returns:
            str: The human-readable strategy name.
        """
        match strategy_type:
            case StrategyType.SWING:
                return "Swing Trading"
            case StrategyType.INTRADAY:
                return "Intraday Trading"
            case StrategyType.SCALPING:
                return "Scalping"
            case StrategyType.OPTION_SCALPING:
                return "Option Scalping"
            case StrategyType.NO_TRADE:
                return "No Trade"
            case _:
                return "Unknown"

    def evaluate_snapshot(self, *args, **kwargs) -> Tuple[MarketEnvironment, StrategyType, str]:
        """
        Evaluates a market snapshot to detect environment, select strategy, and get its name.

        Args:
            *args, **kwargs: The market snapshot or parameters to build one.

        Returns:
            Tuple[MarketEnvironment, StrategyType, str]: The market environment, selected strategy, and strategy name.
        """
        snapshot = args[0] if args else kwargs.get('snapshot', kwargs)
        env: MarketEnvironment = self.detect_market_environment(snapshot)
        strat: StrategyType = self.select_strategy(env)
        strat_name: str = self.get_strategy_name(strat)
        return env, strat, strat_name
