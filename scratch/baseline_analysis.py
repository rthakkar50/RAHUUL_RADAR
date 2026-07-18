import sys, os, json
from collections import Counter
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService
import scanner.scanner_engine as se
import core.master_signal_pipeline as msp

stats_data = []

# Patch MasterSignalPipeline to intercept results
original_run = msp.MasterSignalPipeline.run
def hooked_run(self, *args, **kwargs):
    res = original_run(self, *args, **kwargs)
    
    # kwargs has everything from process_post_scan
    symbol = kwargs.get("symbol")
    decision = kwargs.get("decision")
    
    score = kwargs.get("score")
    confidence = kwargs.get("confidence")
    mtf_data = kwargs.get("mtf_data")
    
    adx_val = kwargs.get("adx", {}).get("score", 0.0)
    avwap_status = kwargs.get("avwap", {}).get("position", "Neutral")
    
    mtf_score = getattr(mtf_data, "confluence_score", 0.0) if mtf_data else 0.0
    mtf_status = getattr(mtf_data, "alignment_status", "No Alignment") if mtf_data else "No Alignment"
    
    stats_data.append({
        "symbol": symbol,
        "raw_decision": decision,
        "final_decision": res.get("status") or res.get("signal") or decision,
        "score": score,
        "confidence": res.get("calibrated_confidence", confidence),
        "mtf_score": mtf_score,
        "mtf_status": mtf_status,
        "adx": adx_val,
        "avwap": avwap_status,
        "reasons": res.get("reasons", [])
    })
    
    return res

msp.MasterSignalPipeline.run = hooked_run

print("Starting Baseline Analysis Scan...")
service = SwingScannerService()
final_results = service.execute_swing_scan()

with open("scratch/baseline_data.json", "w") as f:
    json.dump(stats_data, f, indent=4)

print(f"Recorded {len(stats_data)} stocks.")
