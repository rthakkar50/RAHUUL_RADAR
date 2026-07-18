import sys, os
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService
import pandas as pd

def get_bin(val, bins):
    for b in bins:
        if b[0] <= val <= b[1]:
            return b[2]
    return "Out of bounds"

service = SwingScannerService()

# Monkey patch to capture volume_score because it's not exposed in the final summary dict natively
captured_volumes = {}
original_run = service.pipeline.run
def intercepted_run(*args, **kwargs):
    res = original_run(*args, **kwargs)
    symbol = kwargs.get("symbol", "UNKNOWN")
    vol_score = kwargs.get("volume", {}).get("score", 0.0)
    captured_volumes[symbol] = float(vol_score)
    return res
service.pipeline.run = intercepted_run

res = service.execute_swing_scan()
qualified_results = res.get("qualified_results", [])
scanned_count = res.get("scanned_count", 174)

active_trades = []
for item in qualified_results:
    sym = item.get("Symbol", "UNKNOWN").replace(".NS", "")
    # Some symbols in qualified_results might not have .NS removed, let's keep it safe
    sym_full = item.get("Symbol", "UNKNOWN")
    signal = item.get("Signal", "WATCH")
    if signal not in ("BUY", "SELL"):
        continue
        
    score = float(item.get("Score", 0.0))
    conf = float(item.get("Confidence", 0.0))
    vol = captured_volumes.get(sym_full, 0.0)
    
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
        
    active_trades.append({
        "symbol": sym_full,
        "signal": signal,
        "score": score,
        "confidence": conf,
        "volume_score": vol,
        "execution_status": item.get("Execution Status", ""),
        "execution_reason": item.get("Execution Reason", ""),
        "rr": rr
    })

print(f"\nTotal Scanned: {scanned_count}")
buy_count = sum(1 for t in active_trades if t['signal'] == "BUY")
sell_count = sum(1 for t in active_trades if t['signal'] == "SELL")
watch_count = scanned_count - buy_count - sell_count # approx
print(f"BUY Signals: {buy_count}")
print(f"SELL Signals: {sell_count}")
print(f"WATCH Signals: {watch_count}")

score_bins = [(0, 49.99, "0-49"), (50, 59.99, "50-59"), (60, 69.99, "60-69"), (70, 74.99, "70-74"), (75, 79.99, "75-79"), (80, 89.99, "80-89"), (90, 100.0, "90-100")]
conf_bins = [(0, 49.99, "0-49"), (50, 59.99, "50-59"), (60, 64.99, "60-64"), (65, 69.99, "65-69"), (70, 74.99, "70-74"), (75, 84.99, "75-84"), (85, 100.0, "85-100")]
vol_bins = [(0, 19.99, "0-19"), (20, 29.99, "20-29"), (30, 39.99, "30-39"), (40, 49.99, "40-49"), (50, 69.99, "50-69"), (70, 100.0, "70-100")]

score_dist = {b[2]: 0 for b in score_bins}
conf_dist = {b[2]: 0 for b in conf_bins}
vol_dist = {b[2]: 0 for b in vol_bins}

borderline = []

# Populate dists
for t in active_trades:
    sb = get_bin(t["score"], score_bins)
    cb = get_bin(t["confidence"], conf_bins)
    vb = get_bin(t["volume_score"], vol_bins)
    
    if sb in score_dist: score_dist[sb] += 1
    if cb in conf_dist: conf_dist[cb] += 1
    if vb in vol_dist: vol_dist[vb] += 1
    
    if (70 <= t["score"] < 75) or (65 <= t["confidence"] < 70) or (35 <= t["volume_score"] < 40):
        if t["execution_status"] != "READY" and t["execution_status"] != "ENTER NOW":
            borderline.append(t)

print("\n--- DISTRIBUTIONS ---")
print("Score:", score_dist)
print("Confidence:", conf_dist)
print("Volume Score:", vol_dist)

print("\n--- BORDERLINE TRADES ---")
for b in borderline:
    print(f"{b['symbol']} ({b['signal']}): Score={b['score']}, Conf={b['confidence']}, Vol={b['volume_score']} -> {b['execution_reason']}")

print("\n--- IMPACT SIMULATION ---")
baseline = sum(1 for t in active_trades if t["score"] >= 75 and t["confidence"] >= 70 and t["rr"] >= 1.8)
baseline_elite = sum(1 for t in active_trades if t["score"] >= 75 and t["confidence"] >= 70 and t["rr"] >= 1.8 and t["execution_status"] in ("READY", "ENTER NOW"))
print(f"Baseline: {baseline} trades pass thresholds, {baseline_elite} survive Elite")

sim_score = sum(1 for t in active_trades if t["score"] >= 70 and t["confidence"] >= 70 and t["rr"] >= 1.8)
sim_score_elite = sum(1 for t in active_trades if t["score"] >= 70 and t["confidence"] >= 70 and t["rr"] >= 1.8 and t["execution_status"] in ("READY", "ENTER NOW"))
print(f"Reduce Score to 70: +{sim_score - baseline} trades pass thresholds, {sim_score_elite} survive Elite")

sim_conf = sum(1 for t in active_trades if t["score"] >= 75 and t["confidence"] >= 65 and t["rr"] >= 1.8)
sim_conf_elite = sum(1 for t in active_trades if t["score"] >= 75 and t["confidence"] >= 65 and t["rr"] >= 1.8 and t["execution_status"] in ("READY", "ENTER NOW"))
print(f"Reduce Confidence to 65: +{sim_conf - baseline} trades pass thresholds, {sim_conf_elite} survive Elite")

# For Volume, Volume threshold is checked inside Elite Selection (execution_status).
# So if we reduce volume threshold from 40 to 35, anyone who failed Elite solely because volume < 40 but had volume >= 35 would now pass.
sim_vol_elite = sum(1 for t in active_trades if t["score"] >= 75 and t["confidence"] >= 70 and t["rr"] >= 1.8 
                    and ((t["execution_status"] in ("READY", "ENTER NOW")) 
                         or (t["execution_reason"] == "Volume confirmation is severely lacking." and t["volume_score"] >= 35)))
print(f"Reduce Volume threshold to 35: +{sim_vol_elite - baseline_elite} trades survive Elite")

