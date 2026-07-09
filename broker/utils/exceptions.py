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
