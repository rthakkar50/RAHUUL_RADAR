from abc import ABC, abstractmethod
from typing import List, Optional
from core.models import ScanResult
from market.data_provider import OHLCV

class BaseTradingEngine(ABC):
    """
    Abstract base class for modular trading engines.
    """
    @abstractmethod
    def scan(self, symbol: str, ohlcv_list: List[OHLCV]) -> Optional[ScanResult]:
        pass

    @abstractmethod
    def generate_signal(self, ohlcv_list: List[OHLCV]) -> str:
        pass

    @abstractmethod
    def calculate_entry(self, ohlcv_list: List[OHLCV], signal: str) -> float:
        pass

    @abstractmethod
    def calculate_stoploss(self, ohlcv_list: List[OHLCV], entry: float, signal: str) -> float:
        pass

    @abstractmethod
    def calculate_targets(self, entry: float, stoploss: float, signal: str) -> tuple[float, float, float]:
        pass

    @abstractmethod
    def calculate_rr(self, entry: float, stoploss: float, target2: float) -> float:
        pass

    @abstractmethod
    def calculate_score(self, ohlcv_list: List[OHLCV]) -> int:
        pass
