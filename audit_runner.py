import sys
import json
from application.swing_scanner_service import SwingScannerService
from market.universe import get_all_symbols

def main():
    print("--- SPRINT-174A AUDIT EXECUTION ---")
    
    universe = get_all_symbols()[:5] # limit to 5 to avoid rate limit for Task 11
    print(f"Test Universe: {universe}")
    
    scanner = SwingScannerService()
    
    # TASK 9: Cache Check before
    try:
        from core.cache_manager import CacheManager
        cm = CacheManager()
        print("\n--- TASK-9: CACHE AUDIT ---")
        print(f"_SCANNER_CACHE Size: {len(cm.store.get('scanner_results', {}))}")
    except Exception as e:
        print(f"Cache Error: {e}")
        
    print("\n--- TASK-2: SCANNING SYMBOLS ---")
    results = scanner.execute_swing_scan()
    qual = results.get('qualified_results', [])
    
    for q in qual:
        print(f"SYMBOL: {q.get('Symbol')} | Score: {q.get('Score')} | Conf: {q.get('Confidence')} | Decision: {q.get('Signal')} | Reason: {q.get('Reason Selected', 'N/A')}")
        
    print("\n--- TASK-6: FILTERS AUDIT ---")
    print(f"Input Count: {results.get('total_universe')}")
    print(f"Output Count (Scanned): {results.get('total_scanned')}")
    print(f"Rejected Count: {results.get('rejected_count')}")
    print(f"Qualified: {results.get('qualified_count')}")
    
main()
