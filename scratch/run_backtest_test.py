import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest.backtest_engine import BacktestEngine

def run():
    engine = BacktestEngine()
    symbols = ["RELIANCE.NS"]
    res = engine.run_backtest(symbols, "2023-01-01", "2023-01-31", timeframe="1d", mode="SWING")
    
    print(f"Total simulated trades: {len(res)}")
    if res:
        print("First trade:", res[0])

if __name__ == "__main__":
    run()
