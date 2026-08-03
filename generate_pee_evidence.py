import sys
import logging
from unittest.mock import patch
from application.swing_scanner_service import SwingScannerService
from core.precision_entry_engine import PrecisionEntryEngine
from core.master_signal_pipeline import MasterSignalPipeline

logging.getLogger().setLevel(logging.CRITICAL)

pee_candidates = []
orig_run = MasterSignalPipeline.run

def hooked_run(self, *args, **kwargs):
    decision = kwargs.get("decision", "WATCH")
    if decision in ["BUY", "STRONG_BUY"]:
        # Reconstruct the trade dict that PEE expects
        score = kwargs.get("trend", {}).get("score", 50)  # Use trend score as a proxy if TQI is missing, actually kwargs has all scores
        # Usually TQI is calculated by EliteSelectionEngine, but let's use the actual score calculated in SwingScanner
        sym = kwargs.get("symbol")
        
        # In real code, the Score passed to PEE is the TQI (which is 0-100)
        tqi_score = 85.0 # Let's fetch it from the kwargs if possible, or just use what we have
        
        pee_candidates.append({
            "Symbol": sym,
            "Signal": decision,
            "Score": tqi_score,
            "Volume": 500000.0, # Approximate volume if we don't have it in kwargs
            "Risk Reward": "1:2.0",
            "Entry": 100.0
        })
    return orig_run(self, *args, **kwargs)

# Wait, if we don't have exact volume and RR, it's NOT EXACT RUNTIME EVIDENCE.
# The user wants exact runtime evidence. 
# We need to run the Intraday Scanner, but intercept BEFORE the network crashes.
