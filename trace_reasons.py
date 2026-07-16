import sys
import logging

class MockLogger:
    def __getattr__(self, item):
        return lambda *args, **kwargs: None

import types
mock_loguru = types.ModuleType("loguru")
mock_loguru.logger = MockLogger()
sys.modules["loguru"] = mock_loguru

class MockPsutilProcess:
    def memory_info(self):
        class Mem:
            rss = 0
        return Mem()
    def cpu_percent(self):
        return 0.0

mock_psutil = types.ModuleType("psutil")
mock_psutil.Process = lambda *args, **kwargs: MockPsutilProcess()
sys.modules["psutil"] = mock_psutil

from config.config import AppConfig
from application.swing_scanner_service import SwingScannerService
from data.stocks import Stock

cfg = AppConfig()
cfg.load()
svc = SwingScannerService()
stock = Stock(symbol="WIPRO.NS", company_name="Wipro", sector="IT", is_fno=True, is_nifty50=False)

import types
from core.decision_explanation_engine import DecisionExplanationEngine

original_explain = DecisionExplanationEngine.explain
captured = None
def tracking_explain(self, signal, confidence, elite_score, raw_reasons):
    global captured
    captured = raw_reasons
    return original_explain(self, signal, confidence, elite_score, raw_reasons)
    
DecisionExplanationEngine.explain = tracking_explain

svc.execute_swing_scan(stock_list=[stock])

if captured:
    for i, r in enumerate(captured):
        print(f"[{i}] {r}")
else:
    print("No reasons captured.")
