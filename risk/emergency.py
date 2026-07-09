import logging
from typing import Callable, List

logger = logging.getLogger("KillSwitch")

class KillSwitch:
    """Monitors account health and emits emergency stop events if hard limits are breached."""
    
    def __init__(self):
        self._triggered = False
        self._callbacks: List[Callable] = []
        
    def register_callback(self, callback: Callable):
        self._callbacks.append(callback)
        
    def check_health(self, total_drawdown: float, max_allowed_drawdown: float):
        if self._triggered:
            return
            
        if total_drawdown >= max_allowed_drawdown:
            self._triggered = True
            logger.critical(f"EMERGENCY KILL SWITCH TRIGGERED! Drawdown: {total_drawdown}% >= {max_allowed_drawdown}%")
            self._fire_callbacks()
            
    def is_triggered(self) -> bool:
        return self._triggered
        
    def reset(self):
        self._triggered = False
        logger.info("Emergency Kill Switch Reset.")
        
    def _fire_callbacks(self):
        for cb in self._callbacks:
            try:
                cb()
            except Exception as e:
                logger.error(f"Error in kill switch callback: {e}")
