import sys, os
from collections import Counter
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService
import scanner.scanner_engine as se
import core.master_signal_pipeline as msp

stats = {
    "signal": Counter()
}

original_evaluate = se.ScannerEngine.mtf_engine.evaluate if hasattr(se.ScannerEngine, 'mtf_engine') else None

def hooked_evaluate(*args, **kwargs):
    return None

def do_scan():
    print("Starting TRUE REGRESSION validation scan...")
    
    # Patch the class-level or constructor-level.
    # Since ScannerEngine sets self.mtf_engine = MtfEngine() in __init__
    # we can patch ScannerEngine.__init__!
    original_init = se.ScannerEngine.__init__
    def hooked_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.mtf_engine.evaluate = hooked_evaluate
    se.ScannerEngine.__init__ = hooked_init
    
    service = SwingScannerService()
    
    # Also patch MasterSignalPipeline to track decisions
    original_run = msp.MasterSignalPipeline.run
    def hooked_run(self, *args, decision="WATCH", confidence=0.0, **kwargs):
        stats["signal"][decision] += 1
        return original_run(self, *args, decision=decision, confidence=confidence, **kwargs)
    msp.MasterSignalPipeline.run = hooked_run
    
    service.execute_swing_scan()
    
    print("\n--- PREVIOUS SCANNER SIGNAL DISTRIBUTION ---")
    for k, v in sorted(stats['signal'].items()):
        print(f"{k}: {v}")

do_scan()
