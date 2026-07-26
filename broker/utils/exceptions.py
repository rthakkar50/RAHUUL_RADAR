class BrokerException(Exception):
    """Base class for all broker related exceptions"""
    pass

class BrokerAuthError(BrokerException):
    """Raised when broker authentication fails"""
    pass

class OrderPlacementError(BrokerException):
    """Raised when an order placement fails"""
    pass

class NetworkTimeoutError(BrokerException):
    """Raised when API request times out"""
    pass

class TokenExpiredError(BrokerException):
    """Raised when session token is expired"""
    pass

class InsufficientFundsError(OrderPlacementError):
    """Raised when account has insufficient funds/margin for order"""
    pass

class MarketClosedError(OrderPlacementError):
    """Raised when order is placed outside market trading hours"""
    pass

class InvalidSymbolError(OrderPlacementError):
    """Raised when security ID / trading symbol is invalid"""
    pass

class ExchangeError(OrderPlacementError):
    """Raised when exchange segment or system rejects order"""
    pass

