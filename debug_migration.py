import sys
from backtest.backtest_orchestrator import BacktestOrchestrator
from backtest.simulated_broker import SimulatedBroker
from backtest.performance_analytics import PerformanceAnalytics

symbols = ["HDFCBANK.NS"]
start_date = "2025-01-01"
end_date = "2025-06-30"

orchestrator = BacktestOrchestrator()
results = orchestrator.run(symbols, start_date, end_date, "1d")

if results:
    broker = SimulatedBroker()
    evaluated_trades = broker.execute_trades(results, n_days=45)
    
    analytics = PerformanceAnalytics()
    metrics = analytics.generate_summary(evaluated_trades)
    print("Metrics:", metrics)
else:
    print("No results")
