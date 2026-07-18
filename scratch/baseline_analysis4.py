import sys, os, json
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService
import core.master_signal_pipeline as msp

stats_data = []

original_process = msp.MasterSignalPipeline.run
def hooked_process(self, r):
    res = original_process(self, r)
    if res:
        engine_score = getattr(r, "adjusted_score", getattr(r, "total_score", 50))
        res["_engine_score"] = engine_score
        res["_raw_decision"] = getattr(r, "decision", "WATCH")
        mtf = getattr(r, "mtf_data", None)
        res["_mtf_score"] = getattr(mtf, "confluence_score", 0) if mtf else 0
        res["_mtf_status"] = getattr(mtf, "alignment_status", "No Alignment") if mtf else "No Alignment"
        stats_data.append(res)
    return res

msp.MasterSignalPipeline.run = hooked_process

print("Running fast baseline scan...")
service = SwingScannerService()
service.execute_swing_scan()

print("Finished scan.")

# Now process the stats_data
score_bins = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
conf_bins = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}

rejections = {
    "Score": 0,
    "Confidence": 0,
    "MTF": 0,
    "Risk": 0,
    "Elite Selection": 0
}

borderline_trades = []

def bin_value(val, bins_dict):
    v = float(val) if val is not None else 0.0
    if v < 20: bins_dict["0-20"] += 1
    elif v < 40: bins_dict["20-40"] += 1
    elif v < 60: bins_dict["40-60"] += 1
    elif v < 80: bins_dict["60-80"] += 1
    else: bins_dict["80-100"] += 1

min_score, min_conf, min_rr = 75.0, 70.0, 1.8

for item in stats_data:
    score = item.get("_engine_score", 0)
    conf = item.get("calibrated_confidence", item.get("confidence", 0))
    if conf == -1: conf = 0
    decision = item.get("_raw_decision")
    
    # Normalization Layer in scanner:
    bullish_score = score
    if decision in ["SELL", "STRONG_SELL"]:
        score = 100 - bullish_score
        
    bin_value(score, score_bins)
    bin_value(conf, conf_bins)
    
    rr = item.get("risk_reward", 2.0)
    mtf_status = item.get("_mtf_status")
    
    is_rejected = False
    
    if decision in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
        rejected_here = False
        if float(conf) < min_conf:
            rejections["Confidence"] += 1
            rejected_here = True
        if float(score) < min_score:
            rejections["Score"] += 1
            rejected_here = True
        if float(rr) < min_rr:
            rejections["Risk"] += 1
            rejected_here = True
        if mtf_status in ["Major Conflict", "No Alignment"]:
            rejections["MTF"] += 1
            rejected_here = True
            
        if not rejected_here and item.get("execution_status") != "READY":
            rejections["Elite Selection"] += 1
            rejected_here = True
            
        is_rejected = rejected_here
            
        # Borderline trades (minimum score 75, min conf 70 for Balanced)
        is_borderline = False
        notes = []
        if 70 <= float(score) < 75:
            is_borderline = True
            notes.append(f"Score missed by {75-float(score):.1f}")
        if 65 <= float(conf) < 70:
            is_borderline = True
            notes.append(f"Conf missed by {70-float(conf):.1f}")
        
        if is_borderline and is_rejected:
            borderline_trades.append(f"{item.get('symbol', 'UNKNOWN')} ({decision}): {', '.join(notes)}")

print("\n--- BASELINE METRICS ---")
print("SCORE DISTRIBUTION")
for k, v in score_bins.items(): print(f"{k}: {v}")
print("\nCONFIDENCE DISTRIBUTION")
for k, v in conf_bins.items(): print(f"{k}: {v}")
print("\nREJECTIONS (Total Occurrences)")
for k, v in rejections.items(): print(f"{k}: {v}")
print("\nBORDERLINE TRADES (Top 15)")
for bt in borderline_trades[:15]: print(bt)

