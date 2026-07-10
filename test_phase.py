import application.swing_scanner_service as svc
from core.models import ScanResult, SignalStrength

item = {
    "Signal": "BUY",
    "Score": 80.0,
    "Confidence": 80.0,
    "Risk Reward": "1:2.0",
    "Trend": "BULLISH",
    "Entry": 100.0,
    "Stop Loss": 98.0,
    "Target 1": 104.0,
    "_raw_data": {"reasons": []}
}

min_score = 75.0
min_conf = 70.0
min_rr = 1.8

signal = item["Signal"]
score = float(item["Score"])
conf = float(item["Confidence"])
rr = float(item["Risk Reward"].replace("1:", ""))
trend = item["Trend"]

if signal in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
    downgrade_reasons = []
    
    if conf < min_conf:
        downgrade_reasons.append("Confidence below directional threshold")
    if score < min_score:
        downgrade_reasons.append(f"Score below directional threshold")
    if rr < min_rr:
        downgrade_reasons.append("RR below minimum threshold")
        
    if downgrade_reasons:
        signal = "WATCH"
        item["Signal"] = "WATCH"
        item["_reasons"] = downgrade_reasons

# PHASE 3: READY / SETUP Signal Promotion
print("BEFORE PHASE 3: signal=", signal)
if signal == "WATCH" and score >= min_score and conf >= min_conf and rr >= min_rr:
    print("INSIDE PHASE 3!")
    
print("AFTER PHASE 3: signal=", signal)
