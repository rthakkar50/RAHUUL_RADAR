import logging
from typing import Optional
from .base.base_broker import BaseBroker
from .dhan.dhan_broker import DhanBroker
from .zerodha.zerodha_broker import ZerodhaBroker
from .angel.angel_broker import AngelBroker
from .fyers.fyers_broker import FyersBroker
from .utils.security import SecurityManager
from .utils.exceptions import BrokerAuthError

logger = logging.getLogger("BrokerManager")

class BrokerManager:
    """Singleton manager for the active broker session."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrokerManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
        
    def _init(self):
        self.active_broker: Optional[BaseBroker] = None
        self.security_manager = SecurityManager()
        self.broker_map = {
            "dhan": DhanBroker,
            "zerodha": ZerodhaBroker,
            "angel": AngelBroker,
            "fyers": FyersBroker
        }
        
    def initialize_broker(self, broker_name: str) -> bool:
        """Initializes a broker instance without logging in yet."""
        broker_class = self.broker_map.get(broker_name.lower())
        if not broker_class:
            logger.error(f"Broker {broker_name} not supported.")
            return False
            
        self.active_broker = broker_class()
        return True
        
    def login_active_broker(self, credentials: dict) -> bool:
        """Logs into the currently initialized broker."""
        if not self.active_broker:
            logger.error("No active broker initialized.")
            return False
            
        try:
            success = self.active_broker.login(credentials)
            if success:
                logger.info("Broker logged in successfully.")
            return success
        except BrokerAuthError as e:
            logger.error(f"Broker Auth Failed: {e}")
            return False
            
    def get_broker(self) -> Optional[BaseBroker]:
        """Returns the active broker instance."""
        return self.active_broker
        
    def reconnect(self) -> bool:
        """Attempts to reconnect using saved tokens."""
        if not self.active_broker:
            return False
        return self.active_broker.refresh_token()
