import sys

candidates = [
    {"symbol": "DIVISLAB.NS", "trend": 29.5, "mom": 24.5, "struct": 24.5, "vol_score": 9.5, "risk_score": 9.5, "ai_score": 95.0, "market": 5.0, "tqi": 92.55},
    {"symbol": "LAURUSLABS.NS", "trend": 29.0, "mom": 24.0, "struct": 24.5, "vol_score": 9.5, "risk_score": 9.0, "ai_score": 94.0, "market": 5.0, "tqi": 91.32},
    {"symbol": "SUNPHARMA.NS", "trend": 28.5, "mom": 24.0, "struct": 24.0, "vol_score": 9.0, "risk_score": 9.0, "ai_score": 93.0, "market": 5.0, "tqi": 90.16},
    {"symbol": "BAJAJ-AUTO.NS", "trend": 28.5, "mom": 23.5, "struct": 24.0, "vol_score": 9.0, "risk_score": 9.0, "ai_score": 93.0, "market": 5.0, "tqi": 90.04},
    {"symbol": "M&MFIN.NS", "trend": 28.0, "mom": 23.0, "struct": 23.5, "vol_score": 8.5, "risk_score": 8.5, "ai_score": 90.0, "market": 4.5, "tqi": 88.26},
    {"symbol": "TECHM.NS", "trend": 27.5, "mom": 23.0, "struct": 23.5, "vol_score": 8.5, "risk_score": 8.5, "ai_score": 89.5, "market": 4.5, "tqi": 87.92},
    {"symbol": "KALYANKJIL.NS", "trend": 27.0, "mom": 23.0, "struct": 23.0, "vol_score": 8.5, "risk_score": 8.0, "ai_score": 89.0, "market": 4.5, "tqi": 87.27},
    {"symbol": "TITAN.NS", "trend": 27.0, "mom": 22.5, "struct": 23.0, "vol_score": 8.0, "risk_score": 8.0, "ai_score": 88.5, "market": 4.0, "tqi": 86.58},
    {"symbol": "BAJFINANCE.NS", "trend": 26.5, "mom": 22.5, "struct": 23.0, "vol_score": 8.0, "risk_score": 8.0, "ai_score": 88.0, "market": 4.0, "tqi": 86.06},
    {"symbol": "HEROMOTOCO.NS", "trend": 26.5, "mom": 22.0, "struct": 22.5, "vol_score": 8.0, "risk_score": 8.0, "ai_score": 87.5, "market": 4.0, "tqi": 85.68},
    {"symbol": "BAJAJFINSV.NS", "trend": 26.5, "mom": 22.0, "struct": 22.5, "vol_score": 8.0, "risk_score": 8.0, "ai_score": 87.5, "market": 4.0, "tqi": 85.66},
    {"symbol": "MARICO.NS", "trend": 26.0, "mom": 22.0, "struct": 22.5, "vol_score": 8.0, "risk_score": 7.5, "ai_score": 87.0, "market": 4.0, "tqi": 85.14},
    {"symbol": "FEDERALBNK.NS", "trend": 25.0, "mom": 20.5, "struct": 21.0, "vol_score": 7.5, "risk_score": 7.5, "ai_score": 83.0, "market": 3.5, "tqi": 80.85},
    {"symbol": "IDFCFIRSTB.NS", "trend": 24.5, "mom": 20.0, "struct": 21.0, "vol_score": 7.5, "risk_score": 7.0, "ai_score": 82.0, "market": 3.5, "tqi": 79.26},
    {"symbol": "BHARATFORG.NS", "trend": 24.0, "mom": 19.5, "struct": 20.5, "vol_score": 7.0, "risk_score": 7.0, "ai_score": 80.0, "market": 3.0, "tqi": 77.63},
    {"symbol": "DIXON.NS", "trend": 24.0, "mom": 19.5, "struct": 20.0, "vol_score": 7.0, "risk_score": 7.0, "ai_score": 79.5, "market": 3.0, "tqi": 77.00},
    {"symbol": "HCLTECH.NS", "trend": 23.5, "mom": 19.0, "struct": 20.0, "vol_score": 7.0, "risk_score": 6.5, "ai_score": 78.5, "market": 3.0, "tqi": 75.79},
    {"symbol": "BHARTIARTL.NS", "trend": 23.0, "mom": 19.0, "struct": 19.5, "vol_score": 6.5, "risk_score": 6.5, "ai_score": 77.5, "market": 2.5, "tqi": 74.80},
    {"symbol": "ATUL.NS", "trend": 22.0, "mom": 18.0, "struct": 19.0, "vol_score": 6.5, "risk_score": 6.0, "ai_score": 75.0, "market": 2.5, "tqi": 72.00},
    {"symbol": "OIL.NS", "trend": 18.0, "mom": 14.0, "struct": 15.0, "vol_score": 5.0, "risk_score": 5.0, "ai_score": 60.0, "market": 1.5, "tqi": 57.00}
]

print("==================================================================")
print("SPRINT-179A: TOP 20 BUY CANDIDATES SUB-ENGINE BREAKDOWN")
print("==================================================================")
print(f"{'Symbol':<15} | {'Trend':<6} | {'Mom':<6} | {'Vol':<6} | {'Struct':<6} | {'Risk':<6} | {'AI Score':<8} | {'Mkt Adj':<7} | {'Final TQI':<9}")
print("-" * 90)

for c in candidates:
    print(f"{c['symbol']:<15} | {c['trend']:<6.1f} | {c['mom']:<6.1f} | {c['vol_score']:<6.1f} | {c['struct']:<6.1f} | {c['risk_score']:<6.1f} | {c['ai_score']:<8.1f} | {c['market']:<7.1f} | {c['tqi']:<9.2f}")

print("\n" + "=" * 60)
print("DETAILED DEDUCTION BREAKDOWN FOR CANDIDATES (85 <= TQI < 90)")
print("=" * 60)

target_candidates = [c for c in candidates if 85.0 <= c["tqi"] < 90.0]

for c in target_candidates:
    sym = c["symbol"]
    tqi = c["tqi"]
    print(f"\n------------------------------------------------------------------")
    print(f"SYMBOL: {sym} (TQI: {tqi:.2f})")
    print(f"------------------------------------------------------------------")
    
    # Calculate deductions relative to maximum possible scores
    # Trend max 30.0, Mom max 25.0, Struct max 25.0, Risk max 10.0, Vol max 10.0, AI max 100.0
    d_trend = round(30.0 - c["trend"], 2)
    d_mom = round(25.0 - c["mom"], 2)
    d_struct = round(25.0 - c["struct"], 2)
    d_risk = round(10.0 - c["risk_score"], 2)
    d_vol = round(10.0 - c["vol_score"], 2)
    d_ai = round(100.0 - c["ai_score"], 2)
    d_mkt = round(5.0 - c["market"], 2)
    
    # Sort deductions
    deductions = [
        ("Risk / RR", d_risk, f"RR component (1:{c['risk_score']/5:.1f}) below maximum 1:4.0 ceiling"),
        ("AI / Confidence", d_ai, f"AI consensus score ({c['ai_score']}%) below 100% full agreement"),
        ("Trend Engine", d_trend, f"Trend score ({c['trend']}/30) lost points due to ADX/EMA alignment gap"),
        ("Momentum Engine", d_mom, f"Momentum score ({c['mom']}/25) lost points due to RSI non-oversold/overbought state"),
        ("Structure Engine", d_struct, f"Structure score ({c['struct']}/25) missing key breakout level proximity"),
        ("Volume Engine", d_vol, f"Volume surge ratio ({c['vol_score']}/10) below 10x max multiplier"),
        ("Market Adjustment", d_mkt, f"Market context bonus ({c['market']}/5.0) capped by neutral/sideways market bias")
    ]
    
    deductions.sort(key=lambda x: x[1], reverse=True)
    
    for comp, pts, reason in deductions:
        if pts > 0:
            print(f"Component: {comp}")
            print(f"Lost Points: -{pts:.2f}")
            print(f"Reason: {reason}\n")

