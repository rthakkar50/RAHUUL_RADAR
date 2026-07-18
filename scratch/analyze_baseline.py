import json
from collections import Counter

with open("scratch/baseline_data.json", "r") as f:
    data = json.load(f)

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
    if val is None:
        val = 0.0
    v = float(val)
    if v < 20: bins_dict["0-20"] += 1
    elif v < 40: bins_dict["20-40"] += 1
    elif v < 60: bins_dict["40-60"] += 1
    elif v < 80: bins_dict["60-80"] += 1
    else: bins_dict["80-100"] += 1

for d in data:
    score = d.get("score")
    conf = d.get("confidence")
    
    bin_value(score, score_bins)
    bin_value(conf, conf_bins)
    
    # Check rejection reasons (if any)
    reasons = d.get("reasons", [])
    raw_decision = d.get("raw_decision")
    final_decision = d.get("final_decision")
    
    if final_decision in ["WAIT", "WATCH", "REJECTED"]:
        # If it was downgraded, count why
        for r in reasons:
            r_str = str(r).lower()
            if "score below" in r_str: rejections["Score"] += 1
            if "confidence below" in r_str: rejections["Confidence"] += 1
            if "major conflict" in r_str or "rejected" in r_str: rejections["MTF"] += 1
            if "risk" in r_str or "rr" in r_str: rejections["Risk"] += 1
    
    # Borderline trades (minimum score 75, min conf 70 for Balanced)
    if raw_decision in ["BUY", "SELL"]:
        is_borderline = False
        notes = []
        if score is not None and 70 <= float(score) < 75:
            is_borderline = True
            notes.append(f"Score missed by {75-float(score):.1f}")
        if conf is not None and 65 <= float(conf) < 70:
            is_borderline = True
            notes.append(f"Conf missed by {70-float(conf):.1f}")
        
        if is_borderline and final_decision in ["WATCH", "WAIT", "REJECTED"]:
            borderline_trades.append(f"{d['symbol']} ({raw_decision}): {', '.join(notes)}")

print("SCORE DISTRIBUTION")
for k, v in score_bins.items(): print(f"{k}: {v}")
print("\nCONFIDENCE DISTRIBUTION")
for k, v in conf_bins.items(): print(f"{k}: {v}")
print("\nREJECTIONS")
for k, v in rejections.items(): print(f"{k}: {v}")
print("\nBORDERLINE TRADES")
for bt in borderline_trades[:10]: print(bt)

