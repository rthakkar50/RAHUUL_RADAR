import os
import sys
import logging
from pprint import pprint

# Ensure the root folder is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from market.universe import get_fno_symbols
from application.swing_scanner_service import SwingScannerService
from config.config import AppConfig

logging.basicConfig(level=logging.INFO, format="%(message)s")

def validate_pipeline():
    logging.info("Starting V1.0 FINAL Production Validation Script...")
    
    # 1. Configuration & Symbol Universe Check
    config = AppConfig()
    config.load()
    fno = get_fno_symbols()
    test_symbols = fno[:100]
    
    logging.info(f"Loaded {len(test_symbols)} symbols for testing out of {len(fno)}.")
    
    # 2. Run Scanner Engine (End-to-End)
    service = SwingScannerService()
    
    logging.info("Executing Master Scanner Pipeline (Swing)...")
    results = service.execute_swing_scan()
    
    if not results:
        logging.error("PIPELINE FAILED: No results returned.")
        return False
        
    logging.info(f"Scan complete. Total results processed: {len(results)}")
    
    # 3. Validate Consistency
    failures = 0
    for res in results:
        sym = res.get("symbol", "UNKNOWN")
        
        # Check basic existence
        if "score" not in res or "confidence" not in res:
            logging.error(f"[{sym}] Missing core ranking metrics.")
            failures += 1
            
        # Check duplicate references (confidence should vary)
        if res.get("confidence", 0) in [33.3, 66.7, 100.0]:
            logging.error(f"[{sym}] Legacy bucketed confidence detected: {res.get('confidence')}")
            failures += 1
            
        # Check Analysis Panel bindings
        data = res.get("data", {})
        if not data:
            logging.error(f"[{sym}] Missing Analysis Panel 'data' dictionary.")
            failures += 1
        elif "Market Trend" not in data or "Momentum" not in data:
            logging.error(f"[{sym}] Missing Critical Analysis metrics (Market Trend, Momentum).")
            failures += 1
            
    if failures > 0:
        logging.error(f"PIPELINE VALIDATION FAILED WITH {failures} ERRORS.")
        return False
        
    logging.info("PIPELINE DATA MAPPING AND INTEGRITY: PASSED.")
    return True

if __name__ == "__main__":
    success = validate_pipeline()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
