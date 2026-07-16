#!/usr/bin/env python3
# RAHUUL_RADAR - Swing BUY Debug Tool
# Gujarati helper – place in /Users/pr/RAHUUL_RADAR/ and run: python swing_buy_debug.py

import sys
sys.path.insert(0, '.')

print("="*60)
print("RAHUUL_RADAR - SWING BUY DEBUG")
print("="*60)

from application.swing_scanner_service import SwingScannerService
from core.master_signal_pipeline import MasterSignalPipeline
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

svc = SwingScannerService()

# Force Aggressive mode to see more BUYs
print("\n[1] Config check:")
print(f"  swing_signal_mode = {getattr(svc.config, 'swing_signal_mode', 'NOT SET - default Balanced')}")
print("  -> Temporarily setting to Aggressive for debug")
svc.config.swing_signal_mode = 'Aggressive'

# Also lower thresholds manually if needed
print("\n[2] Running FULL swing scan – this takes 1-3 minutes...")
print("  Please wait...")

# Monkey-patch to capture raw signals BEFORE filtering
original_process = None

# Run scan with detailed tracing
try:
    result = svc.execute_swing_scan(progress_callback=lambda p: print(f"  Progress: {p}%", end='\r'))
    
    print("\n\n[3] SCAN COMPLETE")
    print(f"  Total scanned: {result['total_scanned']}")
    print(f"  Qualified: {len(result['qualified_results'])}")
    print(f"  Market Quality: {result['market_quality']}")
    
    from collections import Counter
    signals = Counter([x.get('Signal','') for x in result['qualified_results']])
    print(f"\n  SIGNAL BREAKDOWN:")
    for sig, cnt in signals.most_common():
        print(f"    {sig:15} : {cnt}")
    
    buys = [x for x in result['qualified_results'] if 'BUY' in x.get('Signal','')]
    sells = [x for x in result['qualified_results'] if 'SELL' in x.get('Signal','')]
    watch = [x for x in result['qualified_results'] if x.get('Signal','') == 'WATCH']
    ready = [x for x in result['qualified_results'] if x.get('Signal','') == 'READY']
    
    print(f"\n  BUY/STRONG_BUY : {len(buys)}")
    print(f"  SELL/STRONG_SELL: {len(sells)}")
    print(f"  WATCH          : {len(watch)}")
    print(f"  READY          : {len(ready)}")
    
    if buys:
        print("\n✅ BUY signals FOUND:")
        for b in buys[:5]:
            print(f"  {b['Symbol']:15} | {b['Signal']:12} | Score:{b['Score']} | Conf:{b['Confidence']} | RR:{b['Risk Reward']} | {b['Price']}")
    else:
        print("\n❌ ZERO BUY signals in qualified_results")
        print("\n  Checking WATCH list – why BUYs were downgraded:")
        # Show top WATCH with bullish trend
        bullish_watch = [x for x in watch if 'BULL' in x.get('Trend','').upper()]
        print(f"  Bullish-trend WATCH count: {len(bullish_watch)}")
        for w in bullish_watch[:10]:
            reasons = w.get('_reasons', [])
            print(f"\n  {w['Symbol']:15} | Trend:{w['Trend']:15} | Score:{w['Score']} | Conf:{w['Confidence']} | RR:{w['Risk Reward']}")
            print(f"    Reasons: {', '.join(reasons[:3])}")
            raw = w.get('_raw_data', {})
            print(f"    Entry:{w['Entry']} SL:{w['Stop Loss']} T1:{w['Target 1']}")
    
    # Dump full first 3 WATCH to file for analysis
    import json
    with open('swing_buy_debug_output.json','w') as f:
        json.dump({
            'summary': dict(signals),
            'buys': buys[:10],
            'sells': sells[:10],
            'watch_bullish_sample': bullish_watch[:20]
        }, f, indent=2, default=str)
    print(f"\n  Full debug saved: swing_buy_debug_output.json")
    
    print("\n" + "="*60)
    print("DIAGNOSIS TIPS:")
    print("="*60)
    if len(buys)==0 and len(sells)>0:
        print("1. BUY=0, SELL>0 → Market likely BEARISH right now")
        print("   Check: TrendEngine – is market in BEAR mode?")
        print("")
        print("2. Check config swing_signal_mode:")
        print("   Current forced: Aggressive")
        print("   Your config file may be Conservative → very strict")
        print("   File: config/config.py or config.json")
        print("   Look for: swing_signal_mode")
        print("")
        print("3. Common BUY killers:")
        print("   - Confidence < 65 (Aggressive) / 70 (Balanced) / 75 (Conservative)")
        print("   - Score < 70 / 75 / 80")
        print("   - RR < 1.5 / 1.8 / 2.0")
        print("   - Trade levels invalid: SL >= Entry OR Target <= Entry")
        print("   - Trend = BEAR but Signal = BUY → conflict warning → WATCH")
        print("")
        print("4. QUICK FIX to test:")
        print("   Edit: /Users/pr/RAHUUL_RADAR/config/config.py")
        print("   Set: swing_signal_mode = 'Aggressive'")
        print("   Also check: min_confidence threshold")
        print("")
        print("5. Run with: python run_test.py")
        print("   Check logs/ folder – swing_scanner.log")
    
    print("\nNext step: Send me swing_buy_debug_output.json")
    print("I will tell exact bug line!")
    
except Exception as e:
    import traceback
    print(f"\n❌ ERROR: {e}")
    traceback.print_exc()
    print("\nTry: pip install -r requirements.txt")
