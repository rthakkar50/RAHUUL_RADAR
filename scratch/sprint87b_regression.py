import os
import sys
import json
import copy

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

def set_config_flag(enabled: bool):
    config_path = "/Users/pr/RAHUUL_RADAR/config.json"
    with open(config_path, "r") as f:
        data = json.load(f)
    data["composite_decision_enabled"] = enabled
    # We also limit max_symbols to 5 so it's fast
    data["watchlist_symbols"] = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ITC.NS"]
    data["max_symbols"] = 5
    with open(config_path, "w") as f:
        json.dump(data, f, indent=4)

def run_regression():
    
    provider = YahooFinanceProvider()
    provider.connect()
    trend = TrendEngine()
    momentum = MomentumEngine()
    structure = StructureEngine()
    score = DecisionEngine()
    sector = SectorEngine(provider)
    rs = RelativeStrengthEngine()
    
    # Run OFF
    print("--- SPRINT 87B REGRESSION TEST (FLAG: OFF) ---")
    set_config_flag(False)
    
    scanner1 = ScannerEngine(
        data_provider=provider,
        trend_engine=trend,
        momentum_engine=momentum,
        structure_engine=structure,
        score_engine=score,
        sector_engine=sector,
        relative_strength_engine=rs
    )
    
    app_config = AppConfig()
    app_config.load()
    stock_list = [Stock(symbol=s, company_name=s, sector="NIFTY50", is_fno=True, is_nifty50=True) for s in app_config.watchlist_symbols[:5]]
    
    results1 = scanner1.scan_market(stock_list)
    
    # Run ON
    print("\n--- SPRINT 87B REGRESSION TEST (FLAG: ON) ---")
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
    
    results2 = scanner2.scan_market(stock_list)
    
    # Compare
    print("\n--- COMPARISON ---")
    for r1, r2 in zip(results1, results2):
        if r1.symbol != r2.symbol:
            print(f"Mismatch in symbol order: {r1.symbol} vs {r2.symbol}")
            continue
            
        if r1.signal != r2.signal:
            print(f"[{r1.symbol}] SIGNAL CHANGED: {r1.signal} -> {r2.signal}")
        else:
            print(f"[{r1.symbol}] Signal Match: {r1.signal}")
            
        if r1.total_score != r2.total_score:
            print(f"[{r1.symbol}] SCORE CHANGED: {r1.total_score} -> {r2.total_score}")
            
        # Check reasons for flag ON
        if r2.composite_evaluation:
            print(f"  Composite Reasons ({r2.symbol}):")
            for reason in r2.composite_evaluation.reasons:
                print(f"    - {reason}")
            print(f"  Quality Category: {r2.composite_evaluation.quality_category}")
            
    # Reset config
    set_config_flag(False)

if __name__ == "__main__":
    run_regression()
