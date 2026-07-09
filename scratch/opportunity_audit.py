import os
import sys
import pandas as pd
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backtest.backtest_engine import BacktestDataProvider
from application.intraday_scanner_service import IntradayScannerService
from scanner.scanner_engine import ScannerEngine
from ranking.score_engine import ScoreEngine
from data.stocks import TOP_50_STOCKS, Stock
from core.sector_engine import SectorEngine

def run():
    print("Starting Intraday Opportunity Optimizer Audit...")
    
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=10) # 10 days of 5m data
    
    start_date = start_dt.strftime("%Y-%m-%d")
    end_date = end_dt.strftime("%Y-%m-%d")
    
    timeframe = "5m"
    symbol_list = [s.symbol + ".NS" for s in TOP_50_STOCKS[:20]] # Use top 20 for speed
    
    live_service = IntradayScannerService()
    pipeline = live_service.pipeline
    
    data_provider = BacktestDataProvider(start_date, end_date, timeframe)
    data_provider._fetch_symbol("^NSEI")
    
    watch_candidates = []
    
    for symbol in symbol_list:
        data_provider.set_main_symbol(symbol)
        main_df = data_provider.cache.get(symbol)
        if main_df is None or main_df.empty:
            continue
            
        scanner_engine = ScannerEngine(
            data_provider=data_provider,
            trend_engine=live_service.engines["trend"],
            momentum_engine=live_service.engines["momentum"],
            structure_engine=live_service.engines["structure"],
            score_engine=ScoreEngine(),
            sector_engine=SectorEngine(data_provider)
        )
        
        min_lookback = 50
        trading_days = len(main_df)
        
        if trading_days <= min_lookback + 20:
            continue
            
        stock = Stock(symbol=symbol, company_name=symbol, sector="BACKTEST", is_fno=True, is_nifty50=True)
        
        # We process up to len - 20 to leave 20 candles for forward simulation
        for i in range(min_lookback, trading_days - 20):
            data_provider.current_date_index = i
            current_date = main_df.index[i]
            
            scan_result = scanner_engine.scan_stock(stock)
            if not scan_result:
                continue
                
            price = getattr(scan_result, 'price', 0.0)
            raw_signal = getattr(scan_result, 'signal', None)
            decision_str = str(getattr(raw_signal, 'value', raw_signal)).upper() if raw_signal else "WATCH"
            
            # Map WAIT to WATCH
            if "BUY" in decision_str: decision_str = "BUY"
            elif "SELL" in decision_str: decision_str = "SELL"
            else: decision_str = "WATCH"
            
            reasons = getattr(scan_result, 'reasons', [])
            
            # Run through master pipeline to get full metrics
            try:
                pipeline_res = pipeline.run(
                    symbol=symbol,
                    price=price,
                    decision=decision_str,
                    confidence=getattr(scan_result, 'confidence', 80.0),
                    trend={"score": getattr(scan_result, 'trend_score', 50.0)},
                    momentum={"score": getattr(scan_result, 'momentum_score', 50.0)},
                    structure={"score": getattr(scan_result, 'structure_score', 50.0)},
                    volume={"score": getattr(scan_result, 'volume_score', 50.0)},
                    risk={"score": getattr(scan_result, 'risk_score', 50.0)},
                    relative_strength={"score": getattr(scan_result, 'relative_strength_score', 50.0)}
                )
            except Exception:
                continue
                
            final_decision = pipeline_res.get("decision", decision_str)
            
            score = getattr(scan_result, "adjusted_score", getattr(scan_result, "total_score", 50.0))
            confidence = pipeline_res.get("calibrated_confidence", getattr(scan_result, "confidence", 50.0))
            
            if final_decision in ["WATCH", "WAIT"]:
                # Primary rejection reason
                primary_reason = "Unknown"
                for r in reversed(reasons):
                    if "Downgrading" in r or "Only two engines" in r or "Failed" in r or "Wait" in r:
                        primary_reason = r
                        break
                
                # Check MTCE pipeline output for rejection reasons
                if primary_reason == "Unknown":
                    mtf_status = pipeline_res.get("status", "")
                    if "CONFLICT" in mtf_status.upper():
                        primary_reason = "MTCE Major Conflict"
                    elif "WAIT" in mtf_status.upper():
                        primary_reason = "MTCE Wait for confirmation"
                
                # Forward Simulation
                forward_df = main_df.iloc[i+1:i+21]
                entry_price = forward_df.iloc[0]['Open']
                
                # Assume a hypothetical 0.5% stop loss and 1.0% target for Intraday
                target = entry_price * 1.01
                stop_loss = entry_price * 0.995
                
                outcome = "CHOP"
                for idx, row in forward_df.iterrows():
                    if row['High'] >= target:
                        outcome = "WIN"
                        break
                    elif row['Low'] <= stop_loss:
                        outcome = "LOSS"
                        break
                
                # We classify a "narrowly failed" candidate by high score/confidence
                # Even if it's WATCH, it might have had a decent score
                tqi = (score * 0.45) + (confidence * 0.45) + 10.0 # simplified TQI
                
                watch_candidates.append({
                    "Date": current_date,
                    "Symbol": symbol,
                    "Score": score,
                    "Confidence": confidence,
                    "Trend": getattr(scan_result, 'trend_score', 0),
                    "Momentum": getattr(scan_result, 'momentum_score', 0),
                    "Structure": getattr(scan_result, 'structure_score', 0),
                    "ADX": getattr(scan_result, 'momentum_adx', getattr(scan_result, 'adx', 0)),
                    "TQI": tqi,
                    "Reason": primary_reason,
                    "Outcome": outcome,
                    "RR": "1:2"
                })

    if not watch_candidates:
        print("No WATCH candidates found!")
        sys.exit(0)
        
    df = pd.DataFrame(watch_candidates)
    
    # Sort by Score/Confidence to find top 20 "Narrow Failures"
    df = df.sort_values(by=["Score", "Confidence"], ascending=[False, False])
    top_20 = df.head(20)
    
    reason_counts = df['Reason'].value_counts()
    
    missed_trades = top_20[top_20['Outcome'] == 'WIN']
    correct_rejects = top_20[top_20['Outcome'] == 'LOSS']
    choppy_avoids = top_20[top_20['Outcome'] == 'CHOP']
    
    # Generate Markdown
    md = []
    md.append("# INTRADAY OPPORTUNITY ANALYSIS")
    md.append("")
    md.append("## STEP-1: Top 20 Narrowly Failed WATCH Candidates")
    md.append("")
    md.append("| Symbol | Date | Score | Conf | Trend | Mom | Struct | ADX | TQI | Outcome | Rejection Reason |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|")
    
    for _, row in top_20.iterrows():
        adx_val = row['ADX']
        if isinstance(adx_val, dict):
            adx_val = adx_val.get('value', 0)
        md.append(f"| {row['Symbol']} | {row['Date'].strftime('%Y-%m-%d %H:%M')} | {row['Score']:.1f} | {row['Confidence']:.1f}% | {row['Trend']:.1f} | {row['Momentum']:.1f} | {row['Structure']:.1f} | {adx_val:.1f} | {row['TQI']:.1f} | **{row['Outcome']}** | {row['Reason']} |")
        
    md.append("")
    md.append("## STEP-2: Rejection Reasons Frequency (All WATCH signals)")
    md.append("")
    for reason, count in reason_counts.items():
        md.append(f"- **{count}**: {reason}")
        
    md.append("")
    md.append("## STEP-3 & 4: Opportunity Analysis (Simulation)")
    md.append("")
    md.append("Based on the forward simulation (next 20 candles / 100 minutes) using a strict 1:2 Intraday RR (Target: 1.0%, Stop: 0.5%):")
    md.append("")
    
    md.append(f"### A) Missed High Quality Trades ({len(missed_trades)}/20)")
    md.append("These setups narrowly failed the Base Scanner but would have been highly profitable if executed.")
    for _, row in missed_trades.iterrows():
        md.append(f"- **{row['Symbol']}**: Rejected due to *{row['Reason']}*. Hit Target.")
        
    md.append("")
    md.append(f"### B) Correctly Rejected Trades ({len(correct_rejects)}/20)")
    md.append("These setups were effectively blocked by the filters, saving capital from hitting stop loss.")
    for _, row in correct_rejects.iterrows():
        md.append(f"- **{row['Symbol']}**: Rejected due to *{row['Reason']}*. Avoided Stop Loss.")
        
    md.append("")
    md.append(f"### C) False Breakout / Chop Avoided ({len(choppy_avoids)}/20)")
    md.append("These setups chopped around without hitting either target or stop loss, wasting time and capital efficiency.")
    for _, row in choppy_avoids.iterrows():
        md.append(f"- **{row['Symbol']}**: Rejected due to *{row['Reason']}*. Avoided Chop.")
        
    md.append("")
    md.append("## Conclusion & Optimization Path")
    if len(missed_trades) > len(correct_rejects) + len(choppy_avoids):
        md.append("The filters are **TOO STRICT**. The majority of high-scoring WATCH candidates would have been profitable. Relaxing the primary rejection reason is highly recommended to improve Intraday yield.")
    else:
        md.append("The filters are **FUNCTIONING CORRECTLY**. The majority of high-scoring WATCH candidates would have resulted in losses or chop. The system successfully protects capital. No relaxation is necessary.")
        
    report_path = "/Users/pr/.gemini/antigravity/brain/6fcf3ef8-4bc0-4c18-94e2-4baaf42526ce/INTRADAY_OPPORTUNITY_ANALYSIS.md"
    with open(report_path, "w") as f:
        f.write("\\n".join(md))
        
    print(f"Report generated successfully at {report_path}")

if __name__ == "__main__":
    run()
