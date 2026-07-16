import sys
import os
import io
import re
import time
from PySide6.QtCore import QThread, Signal

class StdoutRedirector(io.StringIO):
    def __init__(self, progress_signal):
        super().__init__()
        self.progress_signal = progress_signal
        
        self.metrics = {
            "buy_win": 0.0,
            "sell_win": 0.0,
            "overall_win": 0.0,
            "profit_factor": 0.0,
            "avg_return": 0.0,
            "exec_time": 0.0
        }

    def write(self, message):
        if "Progress:" in message:
            import re
            match = re.search(r'Progress:\s*(.*?)%?\s*\|\s*ETA:\s*(\d+)s\s*\|\s*(\d+)/(\d+)', message)
            if match:
                try:
                    percent = int(float(match.group(1).replace('%', '')))
                    eta = match.group(2)
                    current = match.group(3)
                    total = match.group(4)
                    text = f"Scanning... {current} / {total} | {percent}% | ETA: {eta}s"
                    self.progress_signal.emit(text, percent)
                except ValueError:
                    pass
            else:
                match = re.search(r'Progress:\s*([\d\.]+)%', message)
                if match:
                    val = float(match.group(1))
                    self.progress_signal.emit(f"Scanning... {int(val)}%", int(val))
                
        # Optional: Keep basic parsing for fallback or other metrics if needed,
        # but the main metrics will be overridden by CSV parsing.
        
    def flush(self):
        pass


class BacktestWrapperThread(QThread):
    progress = Signal(str, int)
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, symbols, start_date, end_date, holding_days):
        super().__init__()
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.holding_days = holding_days
        
    def run(self):
        try:
            from backtest.backtest_orchestrator import BacktestOrchestrator
            from backtest.simulated_broker import SimulatedBroker
            from backtest.performance_analytics import PerformanceAnalytics
            import logging
            
            logging.getLogger("scanner.scanner_engine").setLevel(logging.WARNING)
            logging.getLogger("market.market_engine").setLevel(logging.WARNING)
            
            from config.settings import BASE_DIR
            exports_path = os.path.join(str(BASE_DIR), "exports")
            orchestrator = BacktestOrchestrator()
            
            redirector = StdoutRedirector(self.progress)
            old_stdout = sys.stdout
            sys.stdout = redirector
            
            try:
                start_time = time.time()
                
                results = orchestrator.run(self.symbols, self.start_date, self.end_date, "1d")
                if results:
                    broker = SimulatedBroker()
                    evaluated_trades = broker.execute_trades(results, n_days=self.holding_days)
                    
                    analytics = PerformanceAnalytics(export_dir=exports_path)
                    metrics = analytics.generate_summary(evaluated_trades)
                    analytics.export_to_csv(evaluated_trades)
                    
                    redirector.metrics.update(metrics)
                    redirector.metrics["exec_time"] = round(time.time() - start_time, 2)
                    
                else:
                    self.error.emit("No backtest data found.")
                    return
            except Exception as e:
                self.error.emit(f"Unable to download historical market data. {str(e)}")
                return
            finally:
                sys.stdout = old_stdout
                
            self.finished.emit(redirector.metrics)
            
        except ImportError as e:
            self.error.emit(f"Failed to import original backend: {str(e)}")
        except Exception as e:
            self.error.emit(str(e))

