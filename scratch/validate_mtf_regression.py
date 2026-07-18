import sys, os
from collections import Counter
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService
import core.master_signal_pipeline as msp

stats = {
    "signal": Counter()
}

original_run = msp.MasterSignalPipeline.run

def hooked_run(self, *args, decision="WATCH", confidence=0.0, **kwargs):
    # FORCE DUMMY FALLBACK BY REMOVING MTF_DATA
    if "mtf_data" in kwargs:
        del kwargs["mtf_data"]
    
    result = original_run(self, *args, decision=decision, confidence=confidence, **kwargs)
    
    stats["signal"][decision] += 1
    return result

msp.MasterSignalPipeline.run = hooked_run

def do_scan():
    print("Starting REGRESSION validation scan...")
    service = SwingScannerService()
    service.execute_swing_scan()
    
    print("\n--- PREVIOUS SCANNER SIGNAL DISTRIBUTION ---")
    for k, v in sorted(stats['signal'].items()):
        print(f"{k}: {v}")

do_scan()
