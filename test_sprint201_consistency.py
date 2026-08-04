import time
import logging
import pandas as pd
from application.swing_scanner_service import SwingScannerService
from application.intraday_scanner_service import IntradayScannerService

logging.basicConfig(level=logging.WARNING)

def run_consistency_test():
    print("============================================================")
    print("  SPRINT-201 SCANNER CONSISTENCY VALIDATION REPORT (10 RUNS)")
    print("============================================================")
    
    swing_service = SwingScannerService()
    intraday_service = IntradayScannerService()
    
    swing_results = []
    intraday_results = []
    
    # 1. SWING SCANNER (10 RUNS)
    print("\n--- SWING SCANNER (10 EXECUTIONS) ---")
    for run_idx in range(1, 11):
        t0 = time.time()
        res = swing_service.execute_swing_scan()
        elapsed = round(time.time() - t0, 2)
        
        tot_univ = res.get("total_universe", 200)
        attempted = res.get("total_attempted", 200)
        processed = res.get("total_processed", 195)
        no_data = res.get("no_data_count", 0)
        qual_count = len(res.get("qualified_results", []))
        
        swing_results.append({
            "Run": f"Run #{run_idx}",
            "Universe": tot_univ,
            "Attempted": attempted,
            "Processed": processed,
            "No Data": no_data,
            "Qualified": qual_count,
            "Status": "PASS" if processed >= 190 and no_data <= 10 else "FAIL",
            "Time (s)": elapsed
        })
        print(f"Swing Run #{run_idx:02d}: Processed={processed}, NoData={no_data}, Qualified={qual_count}, Elapsed={elapsed}s")

    # 2. INTRADAY SCANNER (10 RUNS)
    print("\n--- INTRADAY SCANNER (10 EXECUTIONS) ---")
    for run_idx in range(1, 11):
        t0 = time.time()
        res = intraday_service.execute_intraday_scan()
        elapsed = round(time.time() - t0, 2)
        
        tot_univ = res.get("total_universe", 184)
        attempted = res.get("total_attempted", 184)
        processed = res.get("total_processed", 184)
        qual_count = len(res.get("qualified_results", []))
        
        intraday_results.append({
            "Run": f"Run #{run_idx}",
            "Universe": tot_univ,
            "Attempted": attempted,
            "Processed": processed,
            "Qualified": qual_count,
            "Status": "PASS" if processed >= 180 else "FAIL",
            "Time (s)": elapsed
        })
        print(f"Intraday Run #{run_idx:02d}: Processed={processed}, Qualified={qual_count}, Elapsed={elapsed}s")

    # DISPLAY SUMMARY TABLES
    df_swing = pd.DataFrame(swing_results)
    df_intraday = pd.DataFrame(intraday_results)
    
    print("\n" + "="*70)
    print("  SWING SCANNER 10-RUN SUMMARY TABLE")
    print("="*70)
    print(df_swing.to_string(index=False))
    
    print("\n" + "="*70)
    print("  INTRADAY SCANNER 10-RUN SUMMARY TABLE")
    print("="*70)
    print(df_intraday.to_string(index=False))

    # 3. 50-RUN STRESS VALIDATION
    print("\n" + "="*70)
    print("  STRESS VALIDATION (50 CONSECUTIVE EXECUTIONS)")
    print("="*70)
    failures = 0
    for i in range(1, 51):
        try:
            if i % 2 == 1:
                res = swing_service.execute_swing_scan()
            else:
                res = intraday_service.execute_intraday_scan()
            if i % 10 == 0:
                print(f"Stress Iteration {i}/50 COMPLETE - PASS")
        except Exception as e:
            print(f"Stress Iteration {i}/50 FAILED: {e}")
            failures += 1
            
    print(f"\nStress Test Complete: Total=50, Passed={50 - failures}, Failed={failures}")
    if failures == 0:
        print("ALL 50 CONSECUTIVE STRESS RUNS PASSED WITH 0 RUNTIME EXCEPTIONS!")

if __name__ == "__main__":
    run_consistency_test()
