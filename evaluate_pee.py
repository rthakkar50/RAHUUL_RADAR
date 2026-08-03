import re
from core.precision_entry_engine import PrecisionEntryEngine

log_data = """
ENGINE SYMBOL  : ASTRAL.NS
ENGINE SCORE   : 55.5
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : ATUL.NS
ENGINE SCORE   : 72.0
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : BAJAJFINSV.NS
ENGINE SCORE   : 85.66
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : BAJFINANCE.NS
ENGINE SCORE   : 86.06
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : BHARATFORG.NS
ENGINE SCORE   : 77.63
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : BHARTIARTL.NS
ENGINE SCORE   : 74.8
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : DIXON.NS
ENGINE SCORE   : 77.0
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : BAJAJ-AUTO.NS
ENGINE SCORE   : 90.04
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : FEDERALBNK.NS
ENGINE SCORE   : 80.85
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : HCLTECH.NS
ENGINE SCORE   : 75.79
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : HEROMOTOCO.NS
ENGINE SCORE   : 85.68
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : IDFCFIRSTB.NS
ENGINE SCORE   : 79.26
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : IPCALAB.NS
ENGINE SCORE   : 49.5
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : KALYANKJIL.NS
ENGINE SCORE   : 87.27
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : KPITTECH.NS
ENGINE SCORE   : 48.75
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : LAURUSLABS.NS
ENGINE SCORE   : 91.32
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : M&MFIN.NS
ENGINE SCORE   : 88.26
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : MARICO.NS
ENGINE SCORE   : 85.14
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : DIVISLAB.NS
ENGINE SCORE   : 92.55
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : OIL.NS
ENGINE SCORE   : 57.0
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : SUNPHARMA.NS
ENGINE SCORE   : 90.16
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : TECHM.NS
ENGINE SCORE   : 87.92
ENGINE DECISION: BUY
--
ENGINE SYMBOL  : TITAN.NS
ENGINE SCORE   : 86.58
ENGINE DECISION: BUY
"""

pee = PrecisionEntryEngine()

symbols = re.findall(r"ENGINE SYMBOL\s+:\s+(.+)", log_data)
scores = re.findall(r"ENGINE SCORE\s+:\s+([0-9.]+)", log_data)

candidates = []
for sym, score in zip(symbols, scores):
    candidates.append({
        "Symbol": sym,
        "Score": float(score),
        "Signal": "BUY",
        "Volume": 500000.0,
        "Entry": 1000.0,
        "Risk Reward": "1:2.0"
    })

print("=== PEE CANDIDATES ===")
# Take top 20 by score
candidates.sort(key=lambda x: x["Score"], reverse=True)
top20 = candidates[:20]

reached_85 = False

for c in top20:
    res = pee.evaluate(c)
    
    score = c["Score"]
    vol = c["Volume"]
    rr_val = 2.0
    
    rr_points = min(rr_val, 4.0) * 10
    vol_points = min(vol / 200000.0, 1.0) * 10
    bonus_points = 10 if score >= 90 else 0
    final_score = 50.0 + rr_points + vol_points + bonus_points
    
    print("==================================================================")
    print(c["Symbol"])
    print(f"Base = 50")
    print(f"RR = {rr_val} -> +{rr_points:.1f}")
    print(f"Volume = {vol} -> +{vol_points:.1f}")
    print(f"TQI Score = {score}")
    print(f"Score Bonus = +{bonus_points}")
    print(f"Final Entry Score = {final_score:.1f}")
    print(f"Threshold = 85")
    
    decision = 'ENTER NOW' if final_score>=92 else 'RETEST FIRST' if final_score>=85 else 'WAIT' if final_score>=80 else 'REJECT'
    print(f"Decision = {decision}")
    
    if final_score >= 85:
        reached_85 = True

print("==================================================================")
if reached_85:
    print("CONCLUSION: The statement 'Mathematically capped below 85' is FALSE.")
else:
    print("CONCLUSION: No symbol reached >= 85.")
    print("REASON:")
    print("- RR never exceeds 2.0")
    print("- Score bonus missing because TQI was never >= 90")

