"""
RAHUUL RADAR — F&O Engine: Symbol Manager (Task 1 & Task 14)
=============================================================
Dynamic Symbol Universe Manager.
Supports NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, NIFTYNXT50, Stock Futures, Stock Options,
and provides multi-exchange readiness (NSE, BSE, MCX, Crypto Derivatives).
"""

import logging
from typing import Dict, List, Any, Optional
from core.fno_engine.fno_models import FNOContract

logger = logging.getLogger("FNOSymbolManager")


class FNOSymbolManager:
    """
    Dynamic F&O Symbol & Lot Size Registry.
    """

    # Dynamic Lot Size & Strike Step Configuration Map
    INDEX_CONFIG = {
        "NIFTY": {"lot_size": 25, "step": 50.0, "exchange": "NSE"},
        "BANKNIFTY": {"lot_size": 15, "step": 100.0, "exchange": "NSE"},
        "FINNIFTY": {"lot_size": 25, "step": 50.0, "exchange": "NSE"},
        "MIDCPNIFTY": {"lot_size": 50, "step": 25.0, "exchange": "NSE"},
        "NIFTYNXT50": {"lot_size": 10, "step": 100.0, "exchange": "NSE"},
        "BTCUSDT": {"lot_size": 1, "step": 250.0, "exchange": "CRYPTO_DERIVATIVES"},
        "ETHUSDT": {"lot_size": 1, "step": 25.0, "exchange": "CRYPTO_DERIVATIVES"},
        "GOLD": {"lot_size": 100, "step": 100.0, "exchange": "MCX"},
        "CRUDEOIL": {"lot_size": 100, "step": 50.0, "exchange": "MCX"},
    }

    STOCK_LOT_DEFAULTS = {
        "RELIANCE": 250, "TCS": 175, "INFY": 400, "HDFCBANK": 550, "ICICIBANK": 700,
        "SBIN": 1500, "BHARTIARTL": 475, "ITC": 1600, "AXISBANK": 625, "LT": 300,
        "TATAMOTORS": 1425, "TATASTEEL": 5500, "BAJFINANCE": 125, "MARUTI": 100
    }

    def __init__(self):
        self._custom_lots: Dict[str, int] = {}

    def register_custom_symbol(self, symbol: str, lot_size: int, step: float = 10.0, exchange: str = "NSE"):
        """Dynamically registers a custom stock or derivative symbol."""
        symbol_upper = symbol.upper()
        self._custom_lots[symbol_upper] = {
            "lot_size": lot_size,
            "step": step,
            "exchange": exchange
        }

    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Returns symbol metadata (lot size, strike step, exchange)."""
        symbol_upper = symbol.upper()
        if symbol_upper in self.INDEX_CONFIG:
            return self.INDEX_CONFIG[symbol_upper]

        if symbol_upper in self._custom_lots:
            return self._custom_lots[symbol_upper]

        lot_size = self.STOCK_LOT_DEFAULTS.get(symbol_upper, 500)
        return {"lot_size": lot_size, "step": 10.0, "exchange": "NSE"}

    def get_lot_size(self, symbol: str) -> int:
        """Returns lot size for an underlying symbol."""
        return self.get_symbol_info(symbol)["lot_size"]

    def get_strike_step(self, symbol: str) -> float:
        """Returns strike price step size for underlying symbol."""
        return self.get_symbol_info(symbol)["step"]

    def get_exchange(self, symbol: str) -> str:
        """Returns exchange classification (NSE, BSE, MCX, CRYPTO_DERIVATIVES)."""
        return self.get_symbol_info(symbol)["exchange"]

    def get_all_fno_symbols(self) -> List[str]:
        """Returns standard list of supported index & stock F&O symbols."""
        indices = list(FNOSymbolManager.INDEX_CONFIG.keys())
        stocks = list(FNOSymbolManager.STOCK_LOT_DEFAULTS.keys())
        return indices + stocks
