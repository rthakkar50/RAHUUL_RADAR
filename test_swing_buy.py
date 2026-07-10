import sys
import os

from application.swing_scanner_service import SwingScannerService
from core.models import ScanResult, SignalStrength
from data.stocks import Stock
import time

class DummyScannerEngine:
    def scan_market(self, stock_list, mode, progress_callback=None):
        r = ScanResult(
            symbol="RELIANCE.NS",
            company_name="Reliance Industries",
            sector="Energy",
            price=100.0,
            volume=10000,
            trend_direction="STRONG_BULL",
            trend_score=90.0,
            momentum_score=90.0,
            structure_score=90.0,
            volume_score=90.0,
            volatility_score=90.0,
            relative_strength_score=90.0,
            risk_score=90.0,
            mtf_score=90.0,
            total_score=90.0,
            signal=SignalStrength.BUY,
            timestamp=int(time.time())
        )
        r.confidence = 90.0
        r.adjusted_score = 90.0
        r.quality_grade = "A"
        r.breakdown_detail = {"atr": 2.0}
        return [r]

class DummyConfig:
    def __init__(self):
        self.swing_signal_mode = 'Balanced'
    def load(self): pass
    def __getattr__(self, name): return None

svc = SwingScannerService()
svc.config = DummyConfig()

from unittest.mock import patch

with patch('application.swing_scanner_service.ScannerEngine', return_value=DummyScannerEngine()), patch('application.swing_scanner_service.get_all_symbols', return_value=[{"symbol": "RELIANCE.NS", "sector": "Energy", "company_name": "Reliance"}]):
    res = svc.execute_swing_scan()
    print("\n--- RESULTS ---")
    for q in res.get('qualified_results', []):
        print("SYMBOL:", q.get('Symbol'))
        print("SIGNAL:", q.get('Signal'))
        print("SCORE:", q.get('Score'))
        print("CONFIDENCE:", q.get('Confidence'))
        print("REASONS:", q.get('_reasons'))
