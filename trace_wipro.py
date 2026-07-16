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
from scanner.scanner_engine import ScannerEngine
from market.yahoo_provider import YahooFinanceProvider

logging.basicConfig(level=logging.ERROR)

cfg = AppConfig()
cfg.load()
svc = SwingScannerService()
svc.config.swing_signal_mode = 'Balanced'

# Only test WIPRO.NS
stock = Stock(symbol="WIPRO.NS", company_name="Wipro", sector="IT", is_fno=True, is_nifty50=False)

# Let's intercept the key points
print("1. Symbol name: WIPRO.NS")

# 2. DecisionEngine Output
original_calculate = svc.engines["score"]._calibrated_decision_calculate
de_output = None
def tracking_calculate(self, *args, **kwargs):
    global de_output
    res = original_calculate(self, *args, **kwargs)
    de_output = res
    return res
svc.engines["score"]._calibrated_decision_calculate = types.MethodType(tracking_calculate, svc.engines["score"])

# 3. ScanResult
original_scan_market = ScannerEngine.scan_market
scan_result_obj = None
def tracking_scan_market(self, *args, **kwargs):
    global scan_result_obj
    res = original_scan_market(self, *args, **kwargs)
    if res: scan_result_obj = res[0]
    return res
ScannerEngine.scan_market = tracking_scan_market

# Run the execute method manually to capture local variables
original_rank_trades = svc.pipeline.__class__.run
from core.trade_priority_engine import TradePriorityEngine
original_tpe = TradePriorityEngine.rank_trades

tpe_input = None
tpe_output = None
def tracking_tpe(self, trades):
    global tpe_input, tpe_output
    tpe_input = list(trades) # This is qualified_results!
    res = original_tpe(self, trades)
    tpe_output = res
    return res
TradePriorityEngine.rank_trades = tracking_tpe

final_payload = svc.execute_swing_scan(stock_list=[stock])

print(f"2. DecisionEngine output:")
print(f"   Decision: {de_output.decision}")
print(f"   Score: {de_output.score}")
print(f"   Reasons: {de_output.reasons}")

print(f"\n3. ScanResult.signal:")
print(f"   {scan_result_obj.signal}")

post_scan_dict = tpe_input[0] if tpe_input else None
print(f"\n4. process_post_scan() dictionary:")
if post_scan_dict:
    print(f"   (Mapped to dictionary structure, raw decision was SELL)")
else:
    print("   None")

print(f"\n5. qualified_results append:")
if post_scan_dict:
    print(f"   Signal: {post_scan_dict['Signal']}")
    print(f"   Score: {post_scan_dict['Score']}")
    print(f"   Reasons: {post_scan_dict.get('_reasons', [])}")
else:
    print("   (Dropped before append)")

print(f"\n6. TradePriorityEngine output:")
if tpe_output:
    print(f"   Signal: {tpe_output[0]['Signal']}")
    print(f"   Priority Score: {tpe_output[0].get('Priority Score')}")
else:
    print("   Empty")

print(f"\n7. Payload returned by execute_swing_scan():")
if final_payload:
    print(f"   {final_payload[0]['Signal']} (Total payload length: {len(final_payload)})")
else:
    print("   Empty")

