from scanner.scanner_engine import ScannerEngine
from core.models import Stock
from unittest.mock import MagicMock
import pandas as pd
from datetime import datetime

class MockDataProvider:
    def get_ohlcv(self, symbol, interval, period):
        # Generate bearish data
        data = []
        price = 1000
        class MockCandle:
            def __init__(self, p):
                self.timestamp = datetime.now()
                self.open = p + 10
                self.high = p + 15
                self.low = p - 20
                self.close = p - 10
                self.volume = 1000000
        for i in range(100):
            data.append(MockCandle(price))
            price -= 5  # Strong downtrend
        return data

provider = MockDataProvider()
engine = ScannerEngine(data_provider=provider)
res = engine.scan_market([Stock(symbol="TEST", company_name="Test", sector="IT")])
for r in res:
    print(r.signal)
