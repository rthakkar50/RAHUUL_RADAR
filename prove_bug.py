import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from application.swing_scanner_service import SwingScannerService
from unittest.mock import patch

def mock_get_multi_timeframe_data(symbol):
    dates = pd.date_range(end=datetime.now(), periods=100)
    # Create an obvious strong uptrend to guarantee high scores
    close = np.linspace(100, 200, 100) 
    high = close + 5
    low = close - 5
    open_ = close - 2
    vol = np.ones(100) * 100000
    df = pd.DataFrame({'Open': open_, 'High': high, 'Low': low, 'Close': close, 'Volume': vol}, index=dates)
    return df, df, df

class DummyConfig:
    def __init__(self):
        self.swing_signal_mode = 'Balanced'
        self.MIN_BUY_SCORE = 60.0
    def load(self): pass
    def __getattr__(self, name): return None

svc = SwingScannerService()
svc.config = DummyConfig()

# Patch YahooFinanceProvider so we don't get download errors
with patch('market.yahoo_provider.YahooFinanceProvider.get_multi_timeframe_data', side_effect=mock_get_multi_timeframe_data):
    with patch('application.swing_scanner_service.get_all_symbols', return_value=[{"symbol": "TEST.NS", "sector": "Energy", "company_name": "Test"}]):
        res = svc.execute_swing_scan()
        print("\n=== FINAL RESULTS ===")
        for q in res.get('qualified_results', []):
            print("SYMBOL:", q.get('Symbol'))
            print("SIGNAL:", q.get('Signal'))
            print("SCORE:", q.get('Score'))
            print("CONFIDENCE:", q.get('Confidence'))
            print("REASONS:", q.get('_reasons'))
