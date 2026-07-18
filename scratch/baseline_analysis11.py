import sys, os, json
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService
import scanner.scanner_engine as se

original_evaluate = se.ScannerEngine.scan_market
def hooked_evaluate(self, stock_list, *args, **kwargs):
    raw_results = original_evaluate(self, stock_list, *args, **kwargs)
    global my_raw_results
    my_raw_results = raw_results
    return raw_results
se.ScannerEngine.scan_market = hooked_evaluate

service = SwingScannerService()
service.execute_swing_scan()

score_bins = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
conf_bins = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}

rejections = {
    "Score": 0,
    "Confidence": 0,
    "MTF": 0,
    "Risk": 0,
    "Elite Selection": 0
}

borderlines = []

def bin_value(val, bins_dict):
    v = float(val) if val is not None else 0.0
    if v < 20: bins_dict["0-20"] += 1
    elif v < 40: bins_dict["20-40"] += 1
    elif v < 60: bins_dict["40-60"] += 1
    elif v < 80: bins_dict["60-80"] += 1
    else: bins_dict["80-100"] += 1

for r in my_raw_results:
    score = getattr(r, "adjusted_score", getattr(r, "total_score", 50))
    conf = getattr(r, "confidence", 0)
    decision = getattr(r, "decision", "WATCH")
    reasons_list = getattr(r, "reasons", [])
    
    bin_value(score, score_bins)
    bin_value(conf, conf_bins)
    
    # Check what rejected it in the ScoreEngine
    r_str_all = str(reasons_list).lower()
    
    if decision in ["WAIT", "WATCH", "REJECTED"]:
        if "mtce: major conflict" in r_str_all:
            rejections["MTF"] += 1
        elif "failed strict options" in r_str_all or "conditions failed" in r_str_all or "only two engines" in r_str_all:
            rejections["Score"] += 1 # Internal score engine basic drops
            
    # Also check pipeline/post-scan drops for the ones that survived ScoreEngine!
    if decision in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
        # Run pipeline to get Elite Selection reasons
        pipeline_res = service.pipeline.run(
            symbol=r.symbol,
            price=r.price,
            trend={"direction": getattr(r, 'trend_direction', 'SIDEWAYS')},
            momentum={"score": getattr(r, 'momentum_score', 50.0)},
            structure={"score": getattr(r, 'structure_score', 50.0)},
            volume={"score": getattr(r, 'volume_score', 50.0)},
            risk={"score": getattr(r, 'risk_score', 50.0)},
            relative_strength={"score": getattr(r, 'relative_strength_score', 50.0)},
            adx={"score": getattr(r, 'adx_value', 0.0)},
            avwap={"position": getattr(r, 'avwap_status', "Neutral")},
            atr=0.0,
            mtf_data=getattr(r, 'mtf_data', None)
        )
        
        calib_conf = pipeline_res.get("calibrated_confidence", conf)
        if calib_conf is not None: conf = float(calib_conf)
        
        # SPRINT-80 Quality Gates (from execute_swing_scan)
        min_score = 75.0
        min_conf = 70.0
        min_rr = 1.8
        
        entry = float(pipeline_res.get("recommended_entry", 0.0))
        sl = float(pipeline_res.get("stop_loss", 0.0))
        t1 = float(pipeline_res.get("target_1", 0.0))
        
        rr = 2.0
        if entry != 0.0 and sl != 0.0 and t1 != 0.0:
            risk_amt = abs(entry - sl)
            reward_amt = abs(t1 - entry)
            if risk_amt > 0:
                rr = reward_amt / risk_amt
            else:
                rr = float(pipeline_res.get("risk_reward", 2.0))
            
        is_rejected = False
        
        if float(conf) < min_conf:
            rejections["Confidence"] += 1
            is_rejected = True
        if float(score) < min_score:
            rejections["Score"] += 1
            is_rejected = True
        if float(rr) < min_rr:
            rejections["Risk"] += 1
            is_rejected = True
            
        if not is_rejected and pipeline_res.get("execution_status") != "READY":
            rejections["Elite Selection"] += 1
            is_rejected = True
            
        is_borderline = False
        notes = []
        if 70 <= float(score) < 75:
            is_borderline = True
            notes.append(f"Score missed by {75-float(score):.1f}")
        if 65 <= float(conf) < 70:
            is_borderline = True
            notes.append(f"Conf missed by {70-float(conf):.1f}")
            
        if is_borderline and is_rejected:
            borderlines.append(f"{r.symbol} ({decision}): {', '.join(notes)}")

print("\n--- QUALITY GATE CALIBRATION BASELINE ---")
print("\nSCORE DISTRIBUTION")
for k, v in score_bins.items(): print(f"{k}: {v}")
print("\nCONFIDENCE DISTRIBUTION")
for k, v in conf_bins.items(): print(f"{k}: {v}")
print("\nREJECTIONS")
for k, v in rejections.items(): print(f"{k}: {v}")
print("\nBORDERLINE TRADES")
for bt in borderlines[:15]: print(bt)
