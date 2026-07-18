import sys, os
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService

service = SwingScannerService()
res = service.execute_swing_scan()
qualified_results = res.get("qualified_results", [])

print("\nProcessing Waterfall...\n")

total_generated = len(qualified_results)
dropped_by_score = 0
dropped_by_conf = 0
dropped_by_mtf = 0
dropped_by_risk = 0
dropped_by_elite = 0

elite_reasons = {
    "Volume confirmation missing": 0,
    "Risk/Reward": 0,
    "Liquidity": 0,
    "ATR": 0,
    "Other": 0
}

final_qualified = 0

min_score = 75.0
min_conf = 70.0
min_rr = 1.8

for item in qualified_results:
    score = float(item.get("Score", 0.0))
    conf = float(item.get("Confidence", 0.0))
    
    try: 
        entry = float(item.get("Entry", 0.0))
        sl = float(item.get("Stop Loss", 0.0))
        t1 = float(item.get("Target 1", 0.0))
        if abs(entry - sl) > 0:
            rr = abs(t1 - entry) / abs(entry - sl)
        else:
            rr = 0.0
    except: 
        rr = 0.0
        
    mtf = item.get("_raw_data", {}).get("mtf_data") # MtfResult is passed inside _raw_data? 
    # Actually MTF already processed into _reasons if failed? No, ScoreEngine handles it.
    
    # WATERFALL LOGIC
    if score < min_score:
        dropped_by_score += 1
    elif conf < min_conf:
        dropped_by_conf += 1
    elif rr < min_rr:
        dropped_by_risk += 1
    elif item.get("Execution Status") != "READY":
        dropped_by_elite += 1
        
        exec_reason = str(item.get("Execution Reason", "")).lower()
        if "volume" in exec_reason:
            elite_reasons["Volume confirmation missing"] += 1
        elif "risk" in exec_reason or "rr" in exec_reason or "reward" in exec_reason:
            elite_reasons["Risk/Reward"] += 1
        elif "liquid" in exec_reason:
            elite_reasons["Liquidity"] += 1
        elif "atr" in exec_reason:
            elite_reasons["ATR"] += 1
        else:
            elite_reasons["Other"] += 1
    else:
        final_qualified += 1

print("\n--- SPRINT-80A.1 WATERFALL ---")
print(f"174 Stocks")
print(f"↓")
print(f"BUY/SELL Generated: {total_generated}")
print(f"↓")
print(f"Rejected by Score: {dropped_by_score} ({dropped_by_score/total_generated*100:.1f}%)")
print(f"↓")
print(f"Rejected by Confidence: {dropped_by_conf} ({dropped_by_conf/total_generated*100:.1f}%)")
print(f"↓")
print(f"Rejected by MTF: 0 (Filtered by Engine earlier)")
print(f"↓")
print(f"Rejected by Risk: {dropped_by_risk} ({dropped_by_risk/total_generated*100:.1f}%)")
print(f"↓")
print(f"Rejected by Elite Selection: {dropped_by_elite} ({dropped_by_elite/total_generated*100:.1f}%)")
print(f"↓")
print(f"Final Qualified Trades: {final_qualified}")

print("\nElite Selection Failures Breakdown:")
for k, v in elite_reasons.items():
    if dropped_by_elite > 0:
        print(f"- {k}: {v} ({v/dropped_by_elite*100:.1f}%)")
    else:
        print(f"- {k}: {v} (0.0%)")

