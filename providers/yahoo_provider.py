import logging
import yfinance as yf
from providers.retry_manager import RetryManager

logger = logging.getLogger("DataManager")

class YahooProvider:
    def __init__(self):
        self.retry_manager = RetryManager(max_retries=3)
        
    def fetch_stock_data(self, symbol, period="1mo", interval="1d"):
        def _make_request():
            tkr = yf.Ticker(symbol)
            df = tkr.history(period=period, interval=interval)
            if not df.empty:
                return df
            return None
            
        df = self.retry_manager.execute_with_retry(_make_request)
        return df
