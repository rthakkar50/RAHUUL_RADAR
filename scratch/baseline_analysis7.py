import sys, os, json
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService
import scanner.scanner_engine as se

stats_data = []

original_evaluate = se.ScannerEngine.scan_market

def hooked_evaluate(self, stock_list, *args, **kwargs):
    raw_results = original_evaluate(self, stock_list, *args, **kwargs)
    global my_raw_results
    my_raw_results = raw_results
    return raw_results

se.ScannerEngine.scan_market = hooked_evaluate

service = SwingScannerService()
service.execute_swing_scan()

print(f"Intercepted {len(my_raw_results)} results. Processing ALL of them...")

stats_data = []

for r in my_raw_results:
    decision_str = getattr(r, "decision", "WAIT")
    
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
    
    engine_score = getattr(r, "adjusted_score", getattr(r, "total_score", 50))
    score = int(engine_score) if engine_score else 50
    bullish_score = score
    
    if decision_str in ["SELL", "STRONG_SELL"]:
        score = 100 - bullish_score
        
    conf_from_engine = getattr(r, 'confidence', None)
    conf_from_pipeline = pipeline_res.get("calibrated_confidence", None)
    if conf_from_pipeline is not None:
        confidence = float(conf_from_pipeline)
    elif conf_from_engine is not None:
        confidence = float(conf_from_engine)
    else:
        confidence = 0.0
        
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
            
    mtf = getattr(r, "mtf_data", None)
    mtf_status = getattr(mtf, "alignment_status", "No Alignment") if mtf else "No Alignment"
    
    stats_data.append({
        "symbol": r.symbol,
        "raw_decision": decision_str,
        "score": score,
        "confidence": confidence,
        "mtf_status": mtf_status,
        "risk_reward": rr,
        "execution_status": pipeline_res.get("execution_status", "NOT READY")
    })

score_bins = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
conf_bins = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}

rejections = {
    "Score": 0,
    "Confidence": 0,
    "MTF": 0,
    "Risk": 0,
    "Elite Selection": 0,
    "Pre-MTF/ADX Watch/Wait": 0
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
    score = item["score"]
    conf = item["confidence"]
    decision = item["raw_decision"]
    rr = item["risk_reward"]
    mtf_status = item["mtf_status"]
    
    bin_value(score, score_bins)
    bin_value(conf, conf_bins)
    
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
    elif decision in ["WATCH", "WAIT"]:
        rejections["Pre-MTF/ADX Watch/Wait"] += 1

print("\n--- BASELINE METRICS ---")
print("SCORE DISTRIBUTION")
for k, v in score_bins.items(): print(f"{k}: {v}")
print("\nCONFIDENCE DISTRIBUTION")
for k, v in conf_bins.items(): print(f"{k}: {v}")
print("\nREJECTIONS (Total Occurrences)")
for k, v in rejections.items(): print(f"{k}: {v}")
print("\nBORDERLINE TRADES")
for bt in borderline_trades: print(bt)

