import sys, os, json
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService
from data.stocks import Stock

service = SwingScannerService()
fno_data = service.scanner.data_provider.get_fno_symbols()
stock_list = []
for item in fno_data:
    sym = item["symbol"]
    sector = item.get("sector", "F&O")
    company_name = item.get("company_name", sym.replace(".NS", ""))
    stock_list.append(Stock(symbol=sym, company_name=company_name, sector=sector, is_fno=True, is_nifty50=False))

raw_results = service.scanner.evaluate_universe(stock_list)

processed_results = []
for r in raw_results:
    res = service.pipeline.process(r)
    if res:
        res["_engine_score"] = getattr(r, "adjusted_score", getattr(r, "total_score", 50))
        res["_raw_decision"] = r.decision
        res["_mtf_data"] = r.mtf_data
        processed_results.append(res)

stats_data = []
for item in processed_results:
    score = item.get("_engine_score", 0)
    conf = item.get("Confidence", 0)
    
    if item["Signal"] in ["SELL", "STRONG_SELL"]:
        score = 100 - score
        
    decision = item.get("_raw_decision")
    
    mtf = item.get("_mtf_data")
    mtf_score = getattr(mtf, "confluence_score", 0) if mtf else 0
    mtf_status = getattr(mtf, "alignment_status", "No Alignment") if mtf else "No Alignment"
    
    reasons = item.get("_reasons", [])
    
    # Simulate thresholds (Balanced)
    min_score, min_conf, min_rr = 75.0, 70.0, 1.8
    simulated_reasons = []
    if decision in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
        if float(conf) < min_conf: simulated_reasons.append("Confidence")
        if float(score) < min_score: simulated_reasons.append("Score")
        try:
            rr_str = str(item["Risk Reward"]).replace("1:", "").strip()
            rr = float(rr_str) if rr_str and rr_str != "N/A" else 0.0
            if rr < min_rr: simulated_reasons.append("Risk")
        except: pass
        if mtf_status in ["Major Conflict", "No Alignment"]: simulated_reasons.append("MTF")
        if not simulated_reasons and item.get("Execution Status") != "READY":
            simulated_reasons.append("Elite Selection")
            
    stats_data.append({
        "symbol": item["Symbol"],
        "raw_decision": decision,
        "score": score,
        "confidence": conf,
        "mtf_score": mtf_score,
        "mtf_status": mtf_status,
        "reasons": simulated_reasons
    })

with open("scratch/baseline_data.json", "w") as f:
    json.dump(stats_data, f, indent=4)
print("Finished writing baseline_data.json")
