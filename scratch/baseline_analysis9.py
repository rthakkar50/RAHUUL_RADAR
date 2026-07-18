import sys, os, json
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService
from scanner.scanner_engine import ScannerEngine
from core.models.domain_models import ScanResult

def run_analysis():
    service = SwingScannerService()
    scanner = ScannerEngine()
    
    fno_data = scanner.data_provider.get_fno_symbols()
    
    from data.stocks import Stock
    stock_list = []
    for item in fno_data:
        sym = item["symbol"]
        sector = item.get("sector", "F&O")
        company_name = item.get("company_name", sym.replace(".NS", ""))
        stock_list.append(Stock(symbol=sym, company_name=company_name, sector=sector, is_fno=True, is_nifty50=False))

    raw_results = scanner.scan_market(stock_list)
    
    # Process exactly like execute_swing_scan, but keeping everything
    stats_data = []
    for r in raw_results:
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
        
        entry = float(pipeline_res.get("recommended_entry", 0.0))
        sl = float(pipeline_res.get("stop_loss", 0.0))
        t1 = float(pipeline_res.get("target_1", 0.0))
        
        if risk_amt := abs(entry - sl):
            rr = abs(t1 - entry) / risk_amt
        else:
            rr = float(pipeline_res.get("risk_reward", 2.0))
            
        adx_val = getattr(r, 'adx_value', 0.0)
        avwap_status = getattr(r, 'avwap_status', "Neutral")
        
        # Rejections evaluation
        rejected_by = []
        is_borderline = False
        notes = []
        final_decision = decision_str
        
        if score < 50.0 and confidence < 50.0:
            final_decision = "WATCH"
            rejected_by.append("Score/Conf < 50")
        elif decision_str in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
            min_score = 75.0
            min_conf = 70.0
            min_rr = 1.8
            
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
                
            if len(rejected_by) > 0:
                final_decision = "WATCH"
                
            if 70 <= score < 75:
                is_borderline = True
                notes.append(f"Score missed by {75-score:.1f}")
            if 65 <= confidence < 70:
                is_borderline = True
                notes.append(f"Conf missed by {70-confidence:.1f}")
                
        stats_data.append({
            "symbol": r.symbol,
            "raw_decision": decision_str,
            "final_decision": final_decision,
            "score": score,
            "confidence": confidence,
            "mtf_status": mtf_status,
            "adx": adx_val,
            "avwap": avwap_status,
            "rejected_by": rejected_by,
            "is_borderline": is_borderline,
            "borderline_notes": notes
        })

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

    for d in stats_data:
        bin_value(d["score"], score_bins)
        bin_value(d["confidence"], conf_bins)
        
        for r in d["rejected_by"]:
            if r in rejections:
                rejections[r] += 1
                
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

run_analysis()
