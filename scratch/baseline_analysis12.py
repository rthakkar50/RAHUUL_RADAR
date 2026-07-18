import sys, os, json
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService

service = SwingScannerService()
qualified_results = service.execute_swing_scan()

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

for item in qualified_results["qualified_results"]:
    score = item.get("Score", 0)
    conf = item.get("Confidence", 0)
    
    bin_value(score, score_bins)
    bin_value(conf, conf_bins)
    
    reasons = str(item.get("_reasons", [])).lower()
    
    if "score below" in reasons:
        rejections["Score"] += 1
    if "confidence below" in reasons:
        rejections["Confidence"] += 1
    if "mtce:" in reasons and "conflict" in reasons:
        rejections["MTF"] += 1
    if "rr below" in reasons or "invalid" in reasons:
        rejections["Risk"] += 1
    if item.get("Execution Status") != "READY":
        rejections["Elite Selection"] += 1
        
    if 70 <= float(score) < 75 or 65 <= float(conf) < 70:
        if "below" in reasons or item.get("Execution Status") != "READY":
            borderlines.append(f"{item['Symbol']} ({item['Signal']}): Score={score}, Conf={conf}")

print("\n--- QUALITY GATE CALIBRATION BASELINE ---")
print("\nSCORE DISTRIBUTION")
for k, v in score_bins.items(): print(f"{k}: {v}")
print("\nCONFIDENCE DISTRIBUTION")
for k, v in conf_bins.items(): print(f"{k}: {v}")
print("\nREJECTIONS")
for k, v in rejections.items(): print(f"{k}: {v}")
print("\nBORDERLINE TRADES")
for bt in borderlines[:15]: print(bt)

