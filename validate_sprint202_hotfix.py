import sys
import time
import logging
from application.swing_scanner_service import SwingScannerService
from application.intraday_scanner_service import IntradayScannerService
from market.universe import get_all_symbols, get_fno_symbols

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sprint202Validation")

def run_validation():
    print("=" * 70)
    print("      SPRINT-202 CACHE KEY CONSISTENCY HOTFIX VALIDATION")
    print("=" * 70)

    swing_service = SwingScannerService()
    intraday_service = IntradayScannerService()

    swing_runs = []
    print("\n--- RUNNING 5 CONSECUTIVE SWING SCANS ---")
    for i in range(1, 6):
        t0 = time.time()
        results = swing_service.execute_swing_scan(progress_callback=lambda p: None)
        elapsed = time.time() - t0
        
        # Check metrics from yahoo provider
        from market.market_data_manager import MarketDataManager
        mgr = MarketDataManager()
        stats = mgr.yahoo.stats if hasattr(mgr, 'yahoo') and mgr.yahoo else {}
        hits = stats.get('cache_hits', 0)
        misses = stats.get('cache_misses', 0)
        total = hits + misses
        hit_ratio = (hits / total * 100) if total > 0 else 0.0
        
        swing_runs.append({
            "run": i,
            "elapsed_s": round(elapsed, 2),
            "results_len": len(results),
            "cache_hits": hits,
            "cache_misses": misses,
            "hit_ratio": round(hit_ratio, 2)
        })
        print(f"Swing Run {i}: Time={elapsed:.2f}s | Qualified={len(results)} | Hits={hits} | Misses={misses} | Hit Ratio={hit_ratio:.2f}%")

    print("\n--- RUNNING 5 CONSECUTIVE INTRADAY SCANS ---")
    intraday_runs = []
    for i in range(1, 6):
        t0 = time.time()
        results = intraday_service.execute_intraday_scan(timeframe="5m", progress_callback=lambda p: None)
        elapsed = time.time() - t0
        
        intraday_runs.append({
            "run": i,
            "elapsed_s": round(elapsed, 2),
            "results_len": len(results)
        })
        print(f"Intraday Run {i}: Time={elapsed:.2f}s | Results={len(results)}")

    print("\n" + "=" * 70)
    print("                   VALIDATION SUMMARY REPORT")
    print("=" * 70)
    print("\n[Swing Scanner Runs]")
    for r in swing_runs:
        print(f"  Run {r['run']}: Duration={r['elapsed_s']}s, Qualified={r['results_len']}, Hits={r['cache_hits']}, Misses={r['cache_misses']}, HitRatio={r['hit_ratio']}%")

    print("\n[Intraday Scanner Runs]")
    for r in intraday_runs:
        print(f"  Run {r['run']}: Duration={r['elapsed_s']}s, Results={r['results_len']}")

    print("\n[Final Yahoo Provider Metrics (SPRINT-206)]")
    from market.market_data_manager import MarketDataManager
    mgr = MarketDataManager()
    if hasattr(mgr, 'yahoo') and mgr.yahoo:
        st = mgr.yahoo.stats
        print(f"  Total Requests: {st.get('total_requests', 0)}")
        print(f"  Success: {st.get('success', 0)}")
        print(f"  Failure: {st.get('failure', 0)}")
        print(f"  Cache Hits: {st.get('cache_hits', 0)}")
        print(f"  Cache Misses: {st.get('cache_misses', 0)}")
        print(f"  HTTP 429 Count: {st.get('http_429', 0)}")
        print(f"  Reconnect Count: {st.get('reconnect_count', 0)}")
        print(f"  Successful Downloads: {st.get('successful_downloads', 0)}")
        print(f"  Failed / Delisted Symbols: {st.get('failed_symbols', 0)}")
        tot = st.get('cache_hits', 0) + st.get('cache_misses', 0)
        hr = (st.get('cache_hits', 0) / tot * 100) if tot > 0 else 0
        print(f"  Overall Cache Hit Ratio: {hr:.2f}%")

if __name__ == "__main__":
    run_validation()
