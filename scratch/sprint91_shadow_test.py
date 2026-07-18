import os
import sys
import json
import time
from typing import List

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

def set_config_flags(enabled: bool, activation: bool):
    config_path = "/Users/pr/RAHUUL_RADAR/config.json"
    with open(config_path, "r") as f:
        data = json.load(f)
    data["composite_decision_enabled"] = enabled
    data["composite_activation_enabled"] = activation
    
    symbols = ["RELIANCE.NS", "ITC.NS", "HDFCBANK.NS", "INFY.NS", "TCS.NS", "TATAMOTORS.NS", "ZOMATO.NS", "PAYTM.NS"]
    data["watchlist_symbols"] = symbols
    data["max_symbols"] = len(symbols)
    
    with open(config_path, "w") as f:
        json.dump(data, f, indent=4)
        
    return symbols

def run_test():
    provider = YahooFinanceProvider()
    provider.connect()
    trend = TrendEngine()
    momentum = MomentumEngine()
    structure = StructureEngine()
    score = DecisionEngine()
    sector = SectorEngine(provider)
    rs = RelativeStrengthEngine()
    
    scanner = ScannerEngine(
        data_provider=provider,
        trend_engine=trend,
        momentum_engine=momentum,
        structure_engine=structure,
        score_engine=score,
        sector_engine=sector,
        relative_strength_engine=rs
    )
    
    symbols = set_config_flags(True, True)
    stock_list = [Stock(symbol=s, company_name=s, sector="NIFTY50", is_fno=True, is_nifty50=True) for s in symbols]
    
    print("\n--- SPRINT 91: SHADOW MODE TEST (ACTIVATION: ON) ---")
    results = scanner.scan_market(stock_list)
    
    divergence_count = 0
    for r in results:
        if r.composite_evaluation:
            print(f"[{r.symbol}] Legacy: {r.legacy_decision} | New: {r.signal.name} | Quality: {r.composite_evaluation.quality_category}")
            if getattr(r, 'legacy_decision', None) and r.legacy_decision != r.signal.name:
                divergence_count += 1
                
    print(f"\nTotal Divergences: {divergence_count}")
    
    # Restore flags
    set_config_flags(False, False)
    
if __name__ == "__main__":
    run_test()
