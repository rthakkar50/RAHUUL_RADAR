from PySide6.QtCore import QThread, Signal
import time
import logging

logger = logging.getLogger(__name__)

class ScannerWrapperThread(QThread):
    progress = Signal(int)
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def run(self):
        logger.info("Scanner Start")
        try:
            for i in range(1, 101, 20):
                self.progress.emit(i)
                time.sleep(0.1)
            
            results = {
                "total": 5,
                "best_trade": {"symbol": "MOCK", "signal": "BUY", "score": 90},
                "market_health": "Bullish (75/100)",
                "top_buys": [],
                "detail_map": {}
            }
            self.finished.emit(results)
        except Exception as e:
            logger.error(f"Scanner Error: {e}")
            self.error.emit(str(e))
        finally:
            logger.info("Scanner Finish")
