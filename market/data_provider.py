"""
Market data provider interface for RAHUUL_RADAR.
Defines the architectural contract for fetching real-time and historical market data.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class OHLCV:
    """
    Data structure representing a single candlestick (OHLCV).
    """
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

@dataclass
class MarketStatus:
    """
    Data structure representing the current market status.
    """
    is_open: bool
    status_message: str


class MarketDataProvider(ABC):
    """
    Abstract Base Class defining the contract for all market data providers.
    Follows the Dependency Inversion Principle (SOLID).
    Any future API integration (e.g., Dhan, Zerodha) must implement this interface.
    """

    @abstractmethod
    def connect(self) -> bool:
        """
        Establishes a connection to the data provider.
        
        Returns:
            bool: True if connection is successful, False otherwise.
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Closes the connection to the data provider.
        
        Returns:
            bool: True if disconnected successfully, False otherwise.
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Checks if the provider is currently connected.
        
        Returns:
            bool: True if connected, False otherwise.
        """
        pass

    @abstractmethod
    def get_last_price(self, symbol: str) -> float:
        """
        Retrieves the last traded price (LTP) for a symbol.
        
        Args:
            symbol: The stock symbol to query.
            
        Returns:
            float: The last traded price.
        """
        pass

    @abstractmethod
    def get_ohlcv(self, symbol: str) -> List[OHLCV]:
        """
        Retrieves historical or real-time OHLCV data for a symbol.
        
        Args:
            symbol: The stock symbol to query.
            
        Returns:
            List[OHLCV]: A list of candlestick data.
        """
        pass

    @abstractmethod
    def get_volume(self, symbol: str) -> int:
        """
        Retrieves the current daily volume for a symbol.
        
        Args:
            symbol: The stock symbol to query.
            
        Returns:
            int: The total traded volume.
        """
        pass

    @abstractmethod
    def get_market_status(self) -> MarketStatus:
        """
        Retrieves the overall market status (Open, Closed, Pre-Market, etc.).
        
        Returns:
            MarketStatus: The current status of the exchange.
        """
        pass


class MockMarketDataProvider(MarketDataProvider):
    """
    A concrete mock implementation of the MarketDataProvider for development.
    Returns placeholder data without connecting to any real API.
    """

    def __init__(self) -> None:
        self._connected = False

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> bool:
        self._connected = False
        return True

    def is_connected(self) -> bool:
        return self._connected

    def get_last_price(self, symbol: str) -> float:
        return 0.0

    def get_ohlcv(self, symbol: str) -> List[OHLCV]:
        return [
            OHLCV(
                timestamp=datetime.now(),
                open=0.0,
                high=0.0,
                low=0.0,
                close=0.0,
                volume=0
            )
        ]

    def get_volume(self, symbol: str) -> int:
        return 0

    def get_market_status(self) -> MarketStatus:
        return MarketStatus(
            is_open=False,
            status_message="MARKET CLOSED (Placeholder)"
        )
