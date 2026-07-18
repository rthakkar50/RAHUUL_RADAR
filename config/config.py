"""
Configuration loading and validation module.
"""
import os
import json
from typing import List
from config.settings import ENVIRONMENT, LOG_LEVEL, BASE_DIR
from utils.logger import get_logger

logger = get_logger(__name__)

class AppConfig:
    """
    Central configuration manager.
    Follows SOLID by separating configuration loading from application logic.
    """
    
    def __init__(self):
        self.env = ENVIRONMENT
        self.log_level = LOG_LEVEL
        
        # Production defaults
        self.watchlist_symbols: List[str] = [
            "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", 
            "INFY.NS", "TCS.NS", "LT.NS", "AXISBANK.NS", "ONGC.NS", "TATASTEEL.NS"
        ]
        self.is_pro_active: bool = True  # Hardcoded to PRO mode
        self.data_provider: str = "yahoo" # 'yahoo' or 'dhan'
        self.dhan_client_id: str = ""
        self.dhan_access_token: str = ""
        
        self.composite_decision_enabled: bool = False
        self.composite_activation_enabled: bool = False
        self.timeframe: str = "1d"
        self.scan_interval: int = 60
        self.max_symbols: int = 50
        self.debug_mode: bool = False
        self.export_csv: bool = False
        self.export_excel: bool = False
        self.console_colors: bool = True
        self.capital: float = 100000.0
        self.risk_pct: float = 1.0
        
        # Paper Trading Settings
        self.paper_trading_starting_capital: float = 1000000.0
        self.paper_trading_max_open_positions: int = 5
        self.paper_trading_max_exposure_pct: float = 80.0
        self.paper_trading_max_risk_per_trade_pct: float = 1.0
        
        # Quality Gate Thresholds
        self.min_confidence: float = 60.0
        self.min_overall_score: float = 50.0
        self.min_risk_reward: float = 1.5
        self.min_volume_ratio: float = 1.2
        self.min_liquidity: int = 100000
        
        # Scanner Strictness Modes
        self.swing_signal_mode: str = "Balanced"
        self.min_directional_score: float = 75.0
        self.min_directional_confidence: float = 70.0

    def load(self, config_path: str = None) -> None:
        """
        Load configuration from environment, files, or secret managers.
        """
        if config_path is None:
            config_path = os.path.join(str(BASE_DIR), "config.json")
            
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    
                # Safely map JSON properties to instance attributes
                if "watchlist_symbols" in data: self.watchlist_symbols = data["watchlist_symbols"]
                if "timeframe" in data: self.timeframe = data["timeframe"]
                if "scan_interval" in data: self.scan_interval = data["scan_interval"]
                if "max_symbols" in data: self.max_symbols = data["max_symbols"]
                if "composite_decision_enabled" in data: self.composite_decision_enabled = data["composite_decision_enabled"]
                if "composite_activation_enabled" in data: self.composite_activation_enabled = data["composite_activation_enabled"]
                if "debug_mode" in data: self.debug_mode = data["debug_mode"]
                if "log_level" in data: self.log_level = data["log_level"]
                if "export_csv" in data: self.export_csv = data["export_csv"]
                if "export_excel" in data: self.export_excel = data["export_excel"]
                if "console_colors" in data: self.console_colors = data["console_colors"]
                if "data_provider" in data: self.data_provider = data["data_provider"]
                if "dhan_client_id" in data: self.dhan_client_id = data["dhan_client_id"]
                if "dhan_access_token" in data: self.dhan_access_token = data["dhan_access_token"]
                if "telegram_alerts_enabled" in data: self.telegram_alerts_enabled = data["telegram_alerts_enabled"]
                if "telegram_bot_token" in data: self.telegram_bot_token = data["telegram_bot_token"]
                if "telegram_chat_id" in data: self.telegram_chat_id = data["telegram_chat_id"]
                if "capital" in data: self.capital = float(data["capital"])
                if "risk_pct" in data: self.risk_pct = float(data["risk_pct"])
                
                # Paper Trading
                if "paper_trading_starting_capital" in data: self.paper_trading_starting_capital = float(data["paper_trading_starting_capital"])
                if "paper_trading_max_open_positions" in data: self.paper_trading_max_open_positions = int(data["paper_trading_max_open_positions"])
                if "paper_trading_max_exposure_pct" in data: self.paper_trading_max_exposure_pct = float(data["paper_trading_max_exposure_pct"])
                if "paper_trading_max_risk_per_trade_pct" in data: self.paper_trading_max_risk_per_trade_pct = float(data["paper_trading_max_risk_per_trade_pct"])
                
                # Quality Gate Overrides
                if "min_confidence" in data: self.min_confidence = float(data["min_confidence"])
                if "min_overall_score" in data: self.min_overall_score = float(data["min_overall_score"])
                if "min_risk_reward" in data: self.min_risk_reward = float(data["min_risk_reward"])
                if "min_volume_ratio" in data: self.min_volume_ratio = float(data["min_volume_ratio"])
                if "min_liquidity" in data: self.min_liquidity = int(data["min_liquidity"])
                
                if "swing_signal_mode" in data: self.swing_signal_mode = str(data["swing_signal_mode"])
                if "min_directional_score" in data: self.min_directional_score = float(data["min_directional_score"])
                if "min_directional_confidence" in data: self.min_directional_confidence = float(data["min_directional_confidence"])
                
                logger.info(f"Loaded configuration from {config_path}")
            except json.JSONDecodeError as e:
                logger.error(f"Config file '{config_path}' contains invalid JSON: {e}. Using default values.")
            except Exception as e:
                logger.error(f"Failed to load config file '{config_path}': {e}. Using default values.")
        
    def validate(self) -> bool:
        """
        Validate the loaded configuration.
        Reverts invalid values to sensible defaults and logs warnings.
        """
        valid_timeframes = ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        # Validate watchlist
        if not isinstance(self.watchlist_symbols, list) or not all(isinstance(s, str) for s in self.watchlist_symbols):
            logger.warning("Invalid 'watchlist_symbols'. Reverting to default top 10 NSE symbols.")
            self.watchlist_symbols = ["RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "INFY.NS", "TCS.NS", "LT.NS", "AXISBANK.NS", "ONGC.NS", "TATASTEEL.NS"]

        # Validate timeframe
        if not isinstance(self.timeframe, str) or self.timeframe not in valid_timeframes:
            logger.warning(f"Invalid timeframe '{self.timeframe}'. Reverting to '1d'.")
            self.timeframe = "1d"

        # Validate scan interval
        if not isinstance(self.scan_interval, int) or self.scan_interval <= 0:
            logger.warning(f"Invalid scan_interval '{self.scan_interval}'. Reverting to 60 seconds.")
            self.scan_interval = 60

        # Validate max symbols
        if not isinstance(self.max_symbols, int) or self.max_symbols <= 0:
            logger.warning(f"Invalid max_symbols '{self.max_symbols}'. Reverting to 50.")
            self.max_symbols = 50

        # Validate booleans
        if not isinstance(self.debug_mode, bool):
            logger.warning("Invalid debug_mode. Reverting to False.")
            self.debug_mode = False
            
        if not isinstance(self.export_csv, bool):
            logger.warning("Invalid export_csv. Reverting to False.")
            self.export_csv = False
            
        if not isinstance(self.export_excel, bool):
            logger.warning("Invalid export_excel. Reverting to False.")
            self.export_excel = False
            
        if not isinstance(self.console_colors, bool):
            logger.warning("Invalid console_colors. Reverting to True.")
            self.console_colors = True

        # Validate log level
        if not isinstance(self.log_level, str) or self.log_level not in valid_log_levels:
            logger.warning(f"Invalid log_level '{self.log_level}'. Reverting to 'INFO'.")
            self.log_level = "INFO"
            
        return True
