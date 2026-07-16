import sys
sys.path.insert(0, '.')
from collections import Counter

from scanner.scanner_engine import ScannerEngine
from application.swing_scanner_service import SwingScannerService
import application.swing_scanner_service
from core.decision_explanation_engine import DecisionExplanationEngine
import core.decision_explanation_engine

counts = {
    "1_scanner_out": Counter(),
    "2_pre_validate": Counter(),
    "3_post_validate": Counter(),
    "4_post_quality_gate": Counter()
}

original_scan_market = ScannerEngine.scan_market
def patched_scan_market(self, stock_list, mode="SWING", progress_callback=None):
    res = original_scan_market(self, stock_list, mode, progress_callback)
    for r in res:
        sig = getattr(r.signal, 'value', str(r.signal))
        counts["1_scanner_out"][sig] += 1
    return res
ScannerEngine.scan_market = patched_scan_market

original_validate_trade_levels = application.swing_scanner_service.validate_trade_levels
def patched_validate_trade_levels(decision_str, entry, sl, t1):
    counts["2_pre_validate"][decision_str] += 1
    is_valid, reason = original_validate_trade_levels(decision_str, entry, sl, t1)
    if is_valid:
        counts["3_post_validate"][decision_str] += 1
    else:
        counts["3_post_validate"]["WATCH"] += 1
    return is_valid, reason
application.swing_scanner_service.validate_trade_levels = patched_validate_trade_levels

# DecisionExplanationEngine is imported locally in execute_swing_scan!
# So patching the class method is actually correct for stage 4.
original_explain = DecisionExplanationEngine.explain
def patched_explain(self, signal, confidence, elite_score, raw_reasons=None):
    counts["4_post_quality_gate"][signal] += 1
    return original_explain(self, signal, confidence, elite_score, raw_reasons)
DecisionExplanationEngine.explain = patched_explain

def print_counts(stage_name, counter):
    print(f"\n--- {stage_name} ---")
    buys = counter.get('BUY', 0) + counter.get('STRONG_BUY', 0)
    print(f"BUY: {buys}")
    print(f"WATCH: {counter.get('WATCH', 0)}")
    print(f"SELL: {counter.get('SELL', 0) + counter.get('STRONG_SELL', 0)}")
    return buys
    
if __name__ == "__main__":
    print("Running Pipeline Trace v2...")
    svc = SwingScannerService()
    svc.config.swing_signal_mode = 'Aggressive'  
    
    result = svc.execute_swing_scan()
    
    last_buy_count = print_counts("1. ScannerEngine output", counts["1_scanner_out"])
    
    buy_count = print_counts("2. SwingScannerService input", counts["2_pre_validate"])
    if buy_count < last_buy_count:
        print("STOP! Mismatch found at Stage 2.")
        
    last_buy_count = buy_count
    
    buy_count = print_counts("3. After validate_trade_levels()", counts["3_post_validate"])
    if buy_count < last_buy_count:
        print("STOP! Mismatch found at Stage 3.")
        
    last_buy_count = buy_count
    
    buy_count = print_counts("4. After Quality Gate", counts["4_post_quality_gate"])
    if buy_count < last_buy_count:
        print("STOP! Mismatch found at Stage 4.")
        
    last_buy_count = buy_count
    
    final_counter = Counter([x.get('Signal', '') for x in result['qualified_results']])
    buy_count = print_counts("5. Final GUI payload", final_counter)
    if buy_count < last_buy_count:
        print("STOP! Mismatch found at Stage 5.")
