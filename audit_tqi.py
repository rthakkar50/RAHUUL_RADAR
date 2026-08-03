import re
import sys
import logging
from unittest.mock import patch

# Mock logging to quiet down output
logging.getLogger().setLevel(logging.CRITICAL)

from application.intraday_scanner_service import IntradayScannerService
from core.elite_selection_engine import EliteSelectionEngine
import market.yahoo_provider as yp

# Force cache expiry off to prevent yfinance rate limits
orig_init = yp.YahooFinanceProvider.__init__
def hooked_init(self, *args, **kwargs):
    self.CACHE_EXPIRY = 999999999
    orig_init(self, *args, **kwargs)
yp.YahooFinanceProvider.__init__ = hooked_init

tqi_audit_data = []

orig_evaluate = EliteSelectionEngine.evaluate

def hooked_evaluate(self, result_dict):
    res = orig_evaluate(self, result_dict.copy())
    if res is not None:
        tqi_audit_data.append({
            "Symbol": result_dict.get("Symbol"),
            "Score": float(result_dict.get("Score", 0)),
            "Confidence": float(result_dict.get("Confidence", 0)),
            "Volume": float(result_dict.get("Volume", 0)),
            "Signal": str(result_dict.get("Signal", "")),
            "Risk Reward": str(result_dict.get("Risk Reward", "1:2.0")),
            "TQI": float(res.get("Trade Quality Index", 0)),
            "Raw Dict": result_dict
        })
    return res

with patch('core.elite_selection_engine.EliteSelectionEngine.evaluate', new=hooked_evaluate):
    svc = IntradayScannerService()
    try:
        svc.execute_intraday_scan(progress_callback=lambda x: None)
    except Exception as e:
        pass

print(f"Captured {len(tqi_audit_data)} candidates in ESE.")
