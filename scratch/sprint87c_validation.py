import os
import sys
import json
import time
import psutil
from typing import List

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scanner.scanner_engine import ScannerEngine
from market.yahoo_provider import YahooFinanceProvider
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from core.decision_engine import DecisionEngine
from core.sector_engine import SectorEngine
from core.relative_strength_engine import RelativeStrengthEngine
from data.stocks import Stock
from config.config import AppConfig

def set_config_flag(enabled: bool, is_fno: bool = True):
    config_path = "/Users/pr/RAHUUL_RADAR/config.json"
    with open(config_path, "r") as f:
        data = json.load(f)
    data["composite_decision_enabled"] = enabled
    
    # Use FNO symbols
    from config.config import AppConfig
    # Fallback large list if needed
    symbols = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS", "SBIN.NS", 
        "BHARTIARTL.NS", "BAJFINANCE.NS", "LICHSGFIN.NS", "MARUTI.NS", "AXISBANK.NS",
        "KOTAKBANK.NS", "LT.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ASIANPAINT.NS",
        "TITAN.NS", "SUNPHARMA.NS", "ULTRACEMCO.NS", "WIPRO.NS", "NESTLEIND.NS",
        "ONGC.NS", "POWERGRID.NS", "NTPC.NS", "COALINDIA.NS", "TATAMOTORS.NS",
        "TATASTEEL.NS", "BAJAJFINSV.NS", "JSWSTEEL.NS", "ADANIPORTS.NS",
        "GRASIM.NS", "HCLTECH.NS", "TECHM.NS", "INDUSINDBK.NS", "CIPLA.NS"
    ]
    data["watchlist_symbols"] = symbols
    data["max_symbols"] = len(symbols)
    
    with open(config_path, "w") as f:
        json.dump(data, f, indent=4)
        
    return symbols

def get_memory_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def run_validation():
    print("Initializing components...")
    provider = YahooFinanceProvider()
    provider.connect()
    trend = TrendEngine()
    momentum = MomentumEngine()
    structure = StructureEngine()
    score = DecisionEngine()
    sector = SectorEngine(provider)
    rs = RelativeStrengthEngine()
    
    symbols = set_config_flag(False)
    stock_list = [Stock(symbol=s, company_name=s, sector="NIFTY50", is_fno=True, is_nifty50=True) for s in symbols]
    
    print(f"\n--- RUN A: Composite Framework OFF ({len(stock_list)} symbols) ---")
    
    scanner1 = ScannerEngine(
        data_provider=provider,
        trend_engine=trend,
        momentum_engine=momentum,
        structure_engine=structure,
        score_engine=score,
        sector_engine=sector,
        relative_strength_engine=rs
    )
    
    start_time_a = time.time()
    mem_start_a = get_memory_mb()
    results1 = scanner1.scan_market(stock_list)
    mem_end_a = get_memory_mb()
    end_time_a = time.time()
    
    runtime_a = end_time_a - start_time_a
    avg_time_a = runtime_a / max(1, len(results1))
    mem_diff_a = mem_end_a - mem_start_a
    
    print(f"Run A Complete in {runtime_a:.2f}s | Valid Results: {len(results1)}")
    
    print("\n--- RUN B: Composite Framework ON ---")
    set_config_flag(True)
    
    scanner2 = ScannerEngine(
        data_provider=provider,
        trend_engine=trend,
        momentum_engine=momentum,
        structure_engine=structure,
        score_engine=score,
        sector_engine=sector,
        relative_strength_engine=rs
    )
    
    start_time_b = time.time()
    mem_start_b = get_memory_mb()
    results2 = scanner2.scan_market(stock_list)
    mem_end_b = get_memory_mb()
    end_time_b = time.time()
    
    runtime_b = end_time_b - start_time_b
    avg_time_b = runtime_b / max(1, len(results2))
    mem_diff_b = mem_end_b - mem_start_b
    
    print(f"Run B Complete in {runtime_b:.2f}s | Valid Results: {len(results2)}")
    
    # ---------------------------------------------------------
    # VALIDATION CHECKS
    # ---------------------------------------------------------
    print("\n=======================================================")
    print("VALIDATION REPORT")
    print("=======================================================")
    
    # 1. Decision Parity
    parity_failed = 0
    total = min(len(results1), len(results2))
    
    for r1, r2 in zip(results1, results2):
        if r1.signal != r2.signal or r1.total_score != r2.total_score:
            parity_failed += 1
            print(f"[PARITY FAILURE] {r1.symbol}: A({r1.signal}, {r1.total_score}) != B({r2.signal}, {r2.total_score})")
            
    parity_pct = ((total - parity_failed) / max(1, total)) * 100
    print(f"Decision Parity: {parity_pct:.2f}% ({total - parity_failed}/{total})")
    
    # 2. Explainability Coverage
    explainable_count = 0
    for r in results2:
        if hasattr(r, "composite_evaluation") and r.composite_evaluation is not None:
            explainable_count += 1
            
    explainable_pct = (explainable_count / max(1, len(results2))) * 100
    print(f"Explainability Coverage: {explainable_pct:.2f}% ({explainable_count}/{len(results2)})")
    
    # 3. Performance Overhead
    runtime_diff_pct = ((runtime_b - runtime_a) / max(0.001, runtime_a)) * 100
    print(f"\nPerformance Metrics:")
    print(f"  Run A (OFF): {runtime_a:.2f}s | Avg: {avg_time_a:.3f}s/asset | Mem Delta: {mem_diff_a:.2f} MB")
    print(f"  Run B (ON):  {runtime_b:.2f}s | Avg: {avg_time_b:.3f}s/asset | Mem Delta: {mem_diff_b:.2f} MB")
    print(f"  Overhead:    {runtime_diff_pct:+.2f}% Runtime")
    
    # 4. Serialization
    print("\nSerialization Validation:")
    try:
        if len(results2) > 0:
            sample = results2[0]
            # Convert to dict mimicking CSV export
            export_dict = {
                "Symbol": sample.symbol,
                "Signal": str(sample.signal),
                "Quality": getattr(sample.composite_evaluation, 'quality_category', 'N/A') if sample.composite_evaluation else 'N/A'
            }
            print("  CSV Mapping Success: True")
            print(f"  Sample Map: {export_dict}")
    except Exception as e:
        print(f"  Serialization Error: {e}")
        
    set_config_flag(False)
    
if __name__ == "__main__":
    run_validation()
