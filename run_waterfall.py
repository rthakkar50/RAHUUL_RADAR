import sys
import logging
from unittest.mock import patch
from application.swing_scanner_service import SwingScannerService

logging.getLogger().setLevel(logging.CRITICAL)

# We will intercept the pipeline stages directly to build the waterfall.
waterfall = {
    "Market Data": 200,
    "Trend Filter": 0,
    "Momentum Filter": 0,
    "Volume Filter": 0,
    "Structure Filter": 0,
    "Risk Filter": 0,
    "AI Engine": 0,
    "Elite Selection": 0,
    "Precision Entry": 0,
    "Trade Lock": 0,
    "Signal Orchestrator": 0
}

symbol_traces = {}

# We need to trace 5 specific symbols. We'll capture them as they pass through.
target_symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ITC.NS"]

def main():
    print("Running Waterfall Extraction...")
    svc = SwingScannerService()
    
    # We will use the exact data we just scanned.
    results = svc.execute_swing_scan()
    
    # For now, just dump the actual raw scan result so I can see what dropped.
    print(f"Total Universe: 200")
    print(f"Scanned (Live Data Available): {results.get('total_scanned')}")
    print(f"Qualified: {results.get('qualified_count')}")
    
main()
