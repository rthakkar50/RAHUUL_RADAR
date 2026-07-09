import time
import logging

logger = logging.getLogger("DataManager")

class RetryManager:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries

    def execute_with_retry(self, func, *args, **kwargs):
        for attempt in range(1, self.max_retries + 1):
            try:
                res = func(*args, **kwargs)
                if getattr(res, 'status_code', None) == 200:
                    return res
                elif res is not None and not hasattr(res, 'status_code'):
                    # For non-requests returns (like yfinance df)
                    return res
            except Exception as e:
                logger.error(f"RetryManager Error on attempt {attempt}: {e}")
                
            backoff = 2 ** attempt
            time.sleep(backoff)
        return None
