from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.order import Order, Position, Funds, OrderType

class BaseBroker(ABC):
    """Abstract interface defining the contract for all broker integrations."""
    
    @abstractmethod
    def connect(self) -> bool:
        pass
        
    @abstractmethod
    def disconnect(self):
        pass
        
    @abstractmethod
    def login(self, credentials: dict) -> bool:
        pass
        
    @abstractmethod
    def logout(self) -> bool:
        pass
        
    @abstractmethod
    def refresh_token(self) -> bool:
        pass
        
    @abstractmethod
    def get_profile(self) -> dict:
        pass
        
    @abstractmethod
    def get_funds(self) -> Funds:
        pass
        
    @abstractmethod
    def get_margin(self, symbol: str) -> float:
        pass
        
    @abstractmethod
    def get_holdings(self) -> List[Position]:
        pass
        
    @abstractmethod
    def get_positions(self) -> List[Position]:
        pass
        
    @abstractmethod
    def get_orders(self) -> List[Order]:
        pass
        
    @abstractmethod
    def place_order(self, symbol: str, qty: int, order_type: OrderType, price: float = 0.0, trigger_price: float = 0.0) -> str:
        pass
        
    @abstractmethod
    def modify_order(self, order_id: str, new_qty: int, new_price: float = 0.0) -> bool:
        pass
        
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        pass
        
    @abstractmethod
    def square_off(self, symbol: str) -> bool:
        pass
        
    @abstractmethod
    def get_ltp(self, symbol: str) -> float:
        pass
        
    @abstractmethod
    def search_symbol(self, query: str) -> list:
        pass
