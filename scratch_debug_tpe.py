import sys, os, json
sys.path.append(os.path.abspath('.'))
from application.swing_scanner_service import SwingScannerService
import core.trade_priority_engine

orig_rank = core.trade_priority_engine.TradePriorityEngine.rank_trades

def mock_rank(self, trades):
    from collections import Counter
    c = Counter(t.get("Signal") for t in trades)
    print("BEFORE TPE RANKING:", c)
    return orig_rank(self, trades)

core.trade_priority_engine.TradePriorityEngine.rank_trades = mock_rank

service = SwingScannerService()
print("Executing scan...", flush=True)
service.execute_swing_scan(progress_callback=lambda x: None)
