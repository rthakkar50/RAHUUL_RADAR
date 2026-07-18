import sys
import os
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from market.yahoo_provider import YahooFinanceProvider

dp = YahooFinanceProvider()
dp.connect()

symbols = ["BAJAJ-AUTO.NS", "TECHM.NS", "ABB.NS", "AARTIIND.NS"]
results = []

for sym in symbols:
    data_list = dp.get_ohlcv(sym, interval="5m", period="5d")
    if not data_list:
        continue
        
    df = pd.DataFrame(data_list)
    df.set_index('timestamp', inplace=True)
    df.index = pd.to_datetime(df.index)
    
    high = df['high']
    low = df['low']
    close = df['close']
    
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    
    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
    atr = tr.rolling(14).mean()
    
    df['ATR'] = atr
    
    plus_di = 100 * (plus_dm.ewm(alpha=1/14).mean() / atr)
    minus_di = 100 * (abs(minus_dm).ewm(alpha=1/14).mean() / atr)
    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
    adx = dx.ewm(alpha=1/14).mean()
    
    df['ADX'] = adx
    df['+DI'] = plus_di
    df['-DI'] = minus_di
    
    df['EMA20'] = close.ewm(span=20, adjust=False).mean()
    df['EMA50'] = close.ewm(span=50, adjust=False).mean()
    
    df['Date'] = df.index.date
    
    for date, group in df.groupby('Date'):
        for i in range(len(group) - 12):
            idx = group.index[i]
            row = group.loc[idx]
            
            # Find the condition: Strong Trend Structure (EMA20>EMA50), momentum (+DI>-DI), BUT ADX < 20
            # Also require price > EMA20 to ensure it's not a pullback
            if row['EMA20'] > row['EMA50'] and row['close'] > row['EMA20'] and row['+DI'] > row['-DI'] and row['ADX'] < 20:
                entry_price = row['close']
                atr_val = row['ATR'] if not pd.isna(row['ATR']) else (row['high'] - row['low'])
                stop_loss = entry_price - (atr_val * 1.5)
                target = entry_price + (atr_val * 3.0)
                
                forward_15 = group.iloc[i+1 : i+4]
                forward_30 = group.iloc[i+1 : i+7]
                forward_60 = group.iloc[i+1 : i+13]
                
                max_up = (forward_60['high'].max() - entry_price) / entry_price * 100
                max_down = (entry_price - forward_60['low'].min()) / entry_price * 100
                
                adx_crossed = any(forward_60['ADX'] > 22)
                
                hit_target = any(forward_60['high'] >= target)
                hit_sl = any(forward_60['low'] <= stop_loss)
                
                sl_idx = forward_60.index[forward_60['low'] <= stop_loss].min()
                target_idx = forward_60.index[forward_60['high'] >= target].min()
                
                if pd.isna(sl_idx) and pd.isna(target_idx):
                    result_trade = "NEITHER"
                elif pd.isna(sl_idx):
                    result_trade = "TARGET"
                elif pd.isna(target_idx):
                    result_trade = "STOP_LOSS"
                else:
                    result_trade = "TARGET" if target_idx < sl_idx else "STOP_LOSS"
                
                results.append({
                    'Symbol': sym,
                    'Date': str(idx),
                    'Max Upside %': max_up,
                    'Max Downside %': max_down,
                    'ADX Crossed 22': adx_crossed,
                    'Result': result_trade
                })
                break

print("\n--- REPLAY RESULTS ---")
total = len(results)
false_watch = 0
correct_watch = 0
missed_opp = 0

for r in results:
    print(f"Symbol: {r['Symbol']} | Time: {r['Date']}")
    print(f"Max Upside (60m): {r['Max Upside %']:.2f}% | Max Downside: {r['Max Downside %']:.2f}%")
    print(f"Did ADX cross 22? {'Yes' if r['ADX Crossed 22'] else 'No'}")
    print(f"Trade Result if Taken: {r['Result']}")
    print("-")
    
    if r['Result'] == "TARGET":
        missed_opp += 1
        false_watch += 1
    elif r['Result'] == "STOP_LOSS":
        correct_watch += 1
    else:
        if r['Max Upside %'] > 0.5 and r['Max Downside %'] < 0.3:
            false_watch += 1
        else:
            correct_watch += 1

print("\n--- STATISTICS ---")
print(f"Total Instances Analyzed: {total}")
if total > 0:
    print(f"False WATCH (Good Trades Missed) %: {(false_watch/total)*100:.2f}%")
    print(f"Correct WATCH (Bad/Choppy Trades Avoided) %: {(correct_watch/total)*100:.2f}%")
    print(f"Missed Opportunity (Direct Target Hit) %: {(missed_opp/total)*100:.2f}%")
