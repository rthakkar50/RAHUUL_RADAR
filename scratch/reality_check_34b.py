import os
import sys
from datetime import datetime, timedelta
import logging

sys.path.append("/Users/pr/RAHUUL_RADAR")
from market.universe import get_all_symbols
from backtest.backtest_engine import BacktestEngine
from backtest.trade_evaluator import TradeEvaluator

logging.getLogger().setLevel(logging.CRITICAL)

def run_test(days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    universe = get_all_symbols()
    symbol_list = [item["symbol"] for item in universe][:50]
    
    engine = BacktestEngine(export_dir="exports")
    
    # Suppress output to keep logs clean
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    try:
        results = engine.run_backtest(symbol_list, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), timeframe="5m", hold_days=1, mode="INTRADAY")
    finally:
        sys.stdout = old_stdout
        
    return len(results)

if __name__ == "__main__":
    t5 = run_test(5)
    print(f"5 Days Final Trades: {t5}")
    
    t15 = run_test(15)
    print(f"15 Days Final Trades: {t15}")
    
    # t30 = run_test(30)
    # print(f"30 Days Final Trades: {t30}")
