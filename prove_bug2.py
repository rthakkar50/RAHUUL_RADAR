import time
from datetime import datetime
from application.swing_scanner_service import SwingScannerService
from data.provider import OHLCV
from unittest.mock import patch

def mock_get_ohlcv(symbol, interval="1d", period="3mo"):
    data = []
    base_price = 100.0
    for i in range(100):
        close = base_price * (1.01 ** i)
        o = OHLCV(
            timestamp=int(time.time()) - (100-i)*86400,
            open=close * 0.99,
            high=close * 1.02,
            low=close * 0.98,
            close=close,
            volume=1000000
        )
        data.append(o)
    return data

class DummyConfig:
    def __init__(self):
        self.swing_signal_mode = 'Balanced'
        self.MIN_BUY_SCORE = 60.0
    def load(self): pass
    def __getattr__(self, name): return None

svc = SwingScannerService()
svc.config = DummyConfig()

with patch('market.yahoo_provider.YahooFinanceProvider.get_ohlcv', side_effect=mock_get_ohlcv):
    with patch('market.yahoo_provider.YahooFinanceProvider.pre_cache'):
        with patch('application.swing_scanner_service.get_all_symbols', return_value=[{"symbol": "TEST.NS", "sector": "Energy", "company_name": "Test"}]):
            res = svc.execute_swing_scan()
            print("\n=== FINAL RESULTS ===")
            for q in res.get('qualified_results', []):
                print("SYMBOL:", q.get('Symbol'))
                print("SIGNAL:", q.get('Signal'))
                print("SCORE:", q.get('Score'))
                print("CONFIDENCE:", q.get('Confidence'))
                print("REASONS:", q.get('_reasons'))
