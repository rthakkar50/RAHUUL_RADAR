import sys, os
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

print("\nProcessing Waterfall...\n")

total_generated = 0
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

for r in my_raw_results:
    decision_str = getattr(r, "decision", "WATCH")
    if decision_str not in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
        continue
        
    total_generated += 1
    
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
    score = float(engine_score) if engine_score else 50.0
    if decision_str in ["SELL", "STRONG_SELL"]:
        score = 100.0 - score
        
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
    if risk_amt := abs(entry - sl):
        rr = abs(t1 - entry) / risk_amt
    else:
        rr = float(pipeline_res.get("risk_reward", 2.0))
        
    mtf = getattr(r, 'mtf_data', None)
    mtf_status = getattr(mtf, "alignment_status", "No Alignment") if mtf else "No Alignment"
    
    min_score = 75.0
    min_conf = 70.0
    min_rr = 1.8
    
    # WATERFALL LOGIC (FIRST MATCH WINS)
    if score < min_score:
        dropped_by_score += 1
    elif confidence < min_conf:
        dropped_by_conf += 1
    elif mtf_status in ["Major Conflict", "No Alignment"]:
        dropped_by_mtf += 1
    elif rr < min_rr:
        dropped_by_risk += 1
    elif pipeline_res.get("execution_status") != "READY":
        dropped_by_elite += 1
        
        # Determine elite rejection reason
        exec_reason = str(pipeline_res.get("execution_reason", "")).lower()
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
print(f"Rejected by MTF: {dropped_by_mtf} ({dropped_by_mtf/total_generated*100:.1f}%)")
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

