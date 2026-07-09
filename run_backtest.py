import logging
from backtest.backtest_engine import BacktestEngine
from backtest.trade_evaluator import TradeEvaluator
from utils.logger import get_logger

# Optional: suppress noisy INFO logs from engines if they clutter the stdout progress bar
# (Assuming progress bar is written to stdout)
logging.getLogger("scanner.scanner_engine").setLevel(logging.WARNING)
logging.getLogger("market.market_engine").setLevel(logging.WARNING)

if __name__ == "__main__":
    symbols = ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "RELIANCE.NS", "INFY.NS"]
    start_date = "2025-01-01"
    end_date = "2025-06-30"
    
    engine = BacktestEngine()
    results = engine.run_backtest(symbols, start_date, end_date, "1d")
    
    if results:
        evaluator = TradeEvaluator()
        # MASTER-25: Remove 5-day fixed exit. Set to 45 days as an emergency safety net.
        evaluator.evaluate(results, n_days=45)
    else:
        logger.warning("No results to evaluate.")
