import sys, os, json
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService
from core.models.domain_models import ScanResult
import scanner.scanner_engine as se

# We will hook ScannerEngine.scan_market again, but this time we WILL USE the data!
stats_data = []

original_evaluate = se.ScannerEngine.scan_market
def hooked_evaluate(self, stock_list, *args, **kwargs):
    raw_results = original_evaluate(self, stock_list, *args, **kwargs)
    global my_raw_results
    my_raw_results = raw_results
    return raw_results
se.ScannerEngine.scan_market = hooked_evaluate

service = SwingScannerService()
# THIS will run scan_market and save my_raw_results!
service.execute_swing_scan()

# NOW process my_raw_results manually to see what would happen!
for r in my_raw_results:
    decision_str = getattr(r, "decision", "WATCH")
    if decision_str not in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL", "WATCH"]:
        continue
        
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
        atr=getattr(r, 'atr_value', 0.0),
        mtf_data=getattr(r, 'mtf_data', None)
    )
    
    engine_score = getattr(r, "adjusted_score", getattr(r, "total_score", 50))
    score = float(engine_score) if engine_score else 50.0
    bullish_score = score
    if decision_str in ["SELL", "STRONG_SELL"]:
        score = 100.0 - bullish_score
        
    conf_from_engine = getattr(r, 'confidence', None)
    conf_from_pipeline = pipeline_res.get("calibrated_confidence", None)
    if conf_from_pipeline is not None:
        confidence = float(conf_from_pipeline)
    elif conf_from_engine is not None:
        confidence = float(conf_from_engine)
    else:
        confidence = 0.0
        
    mtf = getattr(r, 'mtf_data', None)
    mtf_status = getattr(mtf, "alignment_status", "No Alignment") if mtf else "No Alignment"
    
    # Eval rejections
    rejected_by = []
    is_borderline = False
    notes = []
    
    if decision_str in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
        min_score = 75.0
        min_conf = 70.0
        
        if confidence < min_conf: rejected_by.append("Confidence")
        if score < min_score: rejected_by.append("Score")
        
        reasons = pipeline_res.get("reasons", [])
        for rsn in reasons:
            r_str = str(rsn).lower()
            if "mtce:" in r_str and "major conflict" in r_str:
                rejected_by.append("MTF")
            if "elite selection" in r_str or "not ready" in r_str:
                rejected_by.append("Elite Selection")
                
        if pipeline_res.get("execution_status") != "READY" and "Elite Selection" not in rejected_by:
            rejected_by.append("Elite Selection")
            
        if 70 <= score < 75:
            is_borderline = True
            notes.append(f"Score missed by {75-score:.1f}")
        if 65 <= confidence < 70:
            is_borderline = True
            notes.append(f"Conf missed by {70-confidence:.1f}")
            
    stats_data.append({
        "symbol": r.symbol,
        "raw_decision": decision_str,
        "score": score,
        "confidence": confidence,
        "rejected_by": rejected_by,
        "is_borderline": is_borderline,
        "borderline_notes": notes
    })

score_bins = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
conf_bins = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
rejections = {"Score": 0, "Confidence": 0, "MTF": 0, "Risk": 0, "Elite Selection": 0}
borderlines = []

def bin_value(val, bins_dict):
    v = float(val) if val is not None else 0.0
    if v < 20: bins_dict["0-20"] += 1
    elif v < 40: bins_dict["20-40"] += 1
    elif v < 60: bins_dict["40-60"] += 1
    elif v < 80: bins_dict["60-80"] += 1
    else: bins_dict["80-100"] += 1

for d in stats_data:
    bin_value(d["score"], score_bins)
    bin_value(d["confidence"], conf_bins)
    
    for r in d["rejected_by"]:
        if r in rejections: rejections[r] += 1
        
    if d["is_borderline"]:
        borderlines.append(f"{d['symbol']} ({d['raw_decision']}): {', '.join(d['borderline_notes'])}")

print("\n--- QUALITY GATE CALIBRATION BASELINE ---")
print("\nSCORE DISTRIBUTION")
for k, v in score_bins.items(): print(f"{k}: {v}")
print("\nCONFIDENCE DISTRIBUTION")
for k, v in conf_bins.items(): print(f"{k}: {v}")
print("\nREJECTIONS")
for k, v in rejections.items(): print(f"{k}: {v}")
print("\nBORDERLINE TRADES")
for bt in borderlines[:15]: print(bt)

