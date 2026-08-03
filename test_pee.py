import sys
import logging
from application.intraday_scanner_service import IntradayScannerService
from core.precision_entry_engine import PrecisionEntryEngine
from unittest.mock import patch

logging.getLogger().setLevel(logging.CRITICAL)

orig_evaluate = PrecisionEntryEngine.evaluate
candidate_count = 0

f = open("pee_output.txt", "w")
f.write("=== PEE CANDIDATES ===\n")

def hooked_evaluate(self, trade_dict):
    global candidate_count
    if "BUY" in str(trade_dict.get("Signal", "")):
        candidate_count += 1
        if candidate_count <= 20:
            c = trade_dict
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
            
            f.write("==================================================================\n")
            f.write(str(c.get("Symbol")) + "\n")
            f.write(f"Base = 50\n")
            f.write(f"RR = {rr_val} -> +{rr_points:.1f}\n")
            f.write(f"Volume = {vol} -> +{vol_points:.1f}\n")
            f.write(f"TQI Score = {score}\n")
            f.write(f"Score Bonus = +{bonus_points}\n")
            f.write(f"Final Entry Score = {final_score:.1f}\n")
            f.write(f"Threshold = 85\n")
            f.write(f"Decision = {'ENTER NOW' if final_score>=92 else 'RETEST FIRST' if final_score>=85 else 'WAIT' if final_score>=80 else 'REJECT'}\n")
            f.flush()
    return orig_evaluate(self, trade_dict)

def main():
    print("Running Intraday Scanner to capture PEE candidates...")
    with patch('core.precision_entry_engine.PrecisionEntryEngine.evaluate', new=hooked_evaluate):
        svc = IntradayScannerService()
        try:
            svc.execute_intraday_scan(progress_callback=lambda x: None)
        except Exception as e:
            pass
    f.close()

main()
