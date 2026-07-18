import sys, os
sys.path.append(os.getcwd())
try:
    from backtest.backtest_engine import BacktestEngine
    engine = BacktestEngine()
    symbols = ["DIVISLAB.NS", "EXIDEIND.NS", "FEDERALBNK.NS", "NTPC.NS"]
    res = engine.run_backtest(symbols, "2025-07-17", "2026-07-17", timeframe="1d", mode="SWING")
    print(f"Total simulated trades: {len(res)}")
    for t in res:
        print(t)
except Exception as e:
    print("Error:", e)
