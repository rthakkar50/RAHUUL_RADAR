import sys
import logging
from unittest.mock import patch
from application.intraday_scanner_service import IntradayScannerService
from core.precision_entry_engine import PrecisionEntryEngine
import market.yahoo_provider as yp

logging.getLogger().setLevel(logging.CRITICAL)

# Force the disk cache to NEVER expire so we don't hit Yahoo limits
orig_init = yp.YahooFinanceProvider.__init__
def hooked_init(self, *args, **kwargs):
    self.CACHE_EXPIRY = 999999999 # Never expire
    orig_init(self, *args, **kwargs)
yp.YahooFinanceProvider.__init__ = hooked_init

orig_evaluate = PrecisionEntryEngine.evaluate
candidates = []

def hooked_evaluate(self, trade_dict):
    if "BUY" in str(trade_dict.get("Signal", "")):
        candidates.append(trade_dict.copy())
    return orig_evaluate(self, trade_dict)

def main():
    print("Running Intraday Scanner without network calls (using forced cache)...")
    with patch('core.precision_entry_engine.PrecisionEntryEngine.evaluate', new=hooked_evaluate):
        svc = IntradayScannerService()
        try:
            svc.execute_intraday_scan(progress_callback=lambda x: None)
        except Exception as e:
            pass # ignore timeouts or connection errors

    print("=== PEE CANDIDATES ===")
    if not candidates:
        print("NO CANDIDATES FOUND.")
    for c in candidates[:20]:
        score = float(c.get("Score", 0))
        vol = float(c.get("Volume", 0))
        rr_str = str(c.get("Risk Reward", "1:2.0"))
        try:
            rr_val = float(rr_str.split(":")[1]) if ":" in rr_str else float(rr_str)
        except:
            rr_val = 2.0
            
        rr_points = min(rr_val, 4.0) * 10
        vol_points = min(vol / 200000.0, 1.0) * 10
        bonus_points = 10 if score >= 90 else 0
        final_score = 50.0 + rr_points + vol_points + bonus_points
        
        print("==================================================================")
        print(c.get("Symbol"))
        print(f"Base = 50")
        print(f"RR = {rr_val} -> +{rr_points:.1f}")
        print(f"Volume = {vol} -> +{vol_points:.1f}")
        print(f"TQI Score = {score}")
        print(f"Score Bonus = +{bonus_points}")
        print(f"Final Entry Score = {final_score:.1f}")
        print(f"Threshold = 85")
        print(f"Decision = {'ENTER NOW' if final_score>=92 else 'RETEST FIRST' if final_score>=85 else 'WAIT' if final_score>=80 else 'REJECT'}")

main()
