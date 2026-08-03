import sys
import logging
from unittest.mock import patch
from application.swing_scanner_service import SwingScannerService

logging.getLogger().setLevel(logging.CRITICAL)

def main():
    print("Running Waterfall Extraction...")
    svc = SwingScannerService()
    results = svc.execute_swing_scan()
    
    print("=== FINAL COUNTS ===")
    print("total_universe:", results.get("total_universe"))
    print("total_scanned:", results.get("total_scanned"))
    print("qualified_count:", results.get("qualified_count"))
    print("filter_rejected_count:", results.get("filter_rejected_count"))
    print("no_data_count:", results.get("no_data_count"))
    print("buy_count:", results.get("buy_count"))
    print("watch_count:", results.get("watch_count"))
    print("sell_count:", results.get("sell_count"))
    print("rejected_count:", results.get("rejected_count"))
    
    # Let's inspect rejection reasons in the pipeline
    # The pipeline sets `pipeline_res["reasons"]` if downgraded
    print("\nQualified Symbols Sample:")
    for r in results.get("qualified_results", [])[:5]:
        print(r.get("Symbol"), r.get("Signal"))

main()
