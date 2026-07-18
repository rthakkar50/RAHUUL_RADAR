import sys, os
import pandas as pd
import yfinance as yf
sys.path.append(os.getcwd())

from scanner.scanner_engine import ScannerEngine
from market.yahoo_provider import YahooFinanceProvider
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from ranking.score_engine import ScoreEngine
from market.data_provider import OHLCV

class MockProvider(YahooFinanceProvider):
    def __init__(self):
        super().__init__()
        self.history_cache = {}
        self.current_end_idx = -1
        
    def preload(self, symbols):
        for sym in symbols:
            df = yf.download(sym, period="1y", progress=False)
            self.history_cache[sym] = df

    def get_ohlcv(self, symbol, interval="1d", period="3mo"):
        df = self.history_cache.get(symbol)
        if df is None or df.empty: return []
        
        sliced = df.iloc[:self.current_end_idx]
        result = []
        for dt, row in sliced.iterrows():
            result.append(OHLCV(
                timestamp=dt,
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume'])
            ))
        return result

provider = MockProvider()
trend = TrendEngine()
momentum = MomentumEngine()
struct = StructureEngine()
score = ScoreEngine()
scanner = ScannerEngine(
    data_provider=provider, 
    trend_engine=trend, 
    momentum_engine=momentum, 
    structure_engine=struct, 
    score_engine=score
)

symbols = ["DIVISLAB.NS", "EXIDEIND.NS", "FEDERALBNK.NS", "NTPC.NS"]
provider.preload(symbols)

for sym in symbols:
    print(f"\nScanning historical timeline for {sym}...")
    df = provider.history_cache[sym]
    if df.empty: continue
    
    found = 0
    for i in range(-200, -5):
        provider.current_end_idx = i
        test_date = df.index[i].date()
        
        try:
            res = scanner.scan_market([sym])
            if not res: continue
            sr = res[0]
            if not sr.is_buy() and sr.signal.name != "SELL": continue
            
            dr = sr.decision_result
            if dr and 75 <= dr.raw_score <= 79:
                entry = float(sr.price)
                future_df = df.iloc[i:i+20]
                
                if sr.is_buy():
                    mfe_val = future_df['High'].max()
                    mae_val = future_df['Low'].min()
                    mfe = (mfe_val - entry) / entry * 100
                    mae = (entry - mae_val) / entry * 100
                    print(f"[{test_date}] BUY | Score {dr.raw_score} Conf {dr.confidence} | Entry {entry:.2f} | MFE {mfe:.2f}% MAE {mae:.2f}%")
                    found += 1
                else:
                    mfe_val = future_df['Low'].min()
                    mae_val = future_df['High'].max()
                    mfe = (entry - mfe_val) / entry * 100
                    mae = (mae_val - entry) / entry * 100
                    print(f"[{test_date}] SELL| Score {dr.raw_score} Conf {dr.confidence} | Entry {entry:.2f} | MFE {mfe:.2f}% MAE {mae:.2f}%")
                    found += 1
                
        except Exception as e:
            pass
            
    if found == 0:
        print(f"No borderline signals found historically for {sym}.")

