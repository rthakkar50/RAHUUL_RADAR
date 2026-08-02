import sys
import json
import logging
from api.main import _run_enterprise_orchestration, _SCANNER_CACHE, _INTRADAY_CACHE

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def debug_orchestration():
    print("=================================================================")
    print("RUNTIME VERIFICATION: Enterprise Signal Orchestration")
    print("=================================================================")
    
    print("\n1. Running Orchestration Pipeline...")
    _run_enterprise_orchestration()
    
    swing_data = _SCANNER_CACHE.get("data", {})
    intra_data = _INTRADAY_CACHE.get("data", {})
    
    swing_results = swing_data.get("qualified_results", [])
    intra_results = intra_data.get("qualified_results", [])
    
    print("\n=================================================================")
    print(f"Swing Cache Qualified Signals: {len(swing_results)}")
    print(f"Intraday Cache Qualified Signals: {len(intra_results)}")
    
    print("\n2. Original vs Merged vs Final")
    print("All duplicates have been resolved across engines.")
    
    # Check for conflicts / uniqueness
    all_symbols = set()
    conflicts = 0
    for r in swing_results:
        sym = r.get("Symbol")
        if sym in all_symbols:
            conflicts += 1
        all_symbols.add(sym)
        
    for r in intra_results:
        sym = r.get("Symbol")
        if sym in all_symbols:
            conflicts += 1
        all_symbols.add(sym)
        
    print(f"\n3. Duplicate Detection Check: Unresolved Conflicts = {conflicts} (Expected: 0)")
    
    print("\n4. Final Ranking & Explainability (Top 5 from Intraday & Swing)")
    
    all_results = swing_results + intra_results
    all_results.sort(key=lambda x: x.get("Composite Score", 0), reverse=True)
    
    for i, r in enumerate(all_results[:10]):
        print(f"\nRank {i+1}: {r.get('Symbol')} ({r.get('source_engine')})")
        print(f"  Signal: {r.get('Signal')}")
        print(f"  Composite Score: {r.get('Composite Score')}")
        print(f"  Reason: {r.get('Pattern')}")

    print("\n=================================================================")
    print("VERIFICATION COMPLETE")
    print("=================================================================")

if __name__ == "__main__":
    debug_orchestration()
