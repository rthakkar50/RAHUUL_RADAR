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
            from backtest.backtest_engine import BacktestEngine
            from backtest.trade_evaluator import TradeEvaluator
            import logging
            
            logging.getLogger("scanner.scanner_engine").setLevel(logging.WARNING)
            logging.getLogger("market.market_engine").setLevel(logging.WARNING)
            
            from config.settings import BASE_DIR
            exports_path = os.path.join(str(BASE_DIR), "exports")
            engine = BacktestEngine(export_dir=exports_path)
            
            redirector = StdoutRedirector(self.progress)
            old_stdout = sys.stdout
            sys.stdout = redirector
            
            try:
                start_time = time.time()
                
                results = engine.run_backtest(self.symbols, self.start_date, self.end_date, "1d")
                if results:
                    evaluator = TradeEvaluator(export_dir=exports_path)
                    evaluator.evaluate(results, n_days=self.holding_days)
                    
                    # Calculate metrics directly from completed CSV trades
                    self.calculate_metrics_from_csv(exports_path, redirector)
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

    def calculate_metrics_from_csv(self, exports_path, redirector):
        import glob
        import csv
        
        # Find the most recently created CSV file
        list_of_files = glob.glob(os.path.join(exports_path, 'simulated_trades_*.csv'))
        if not list_of_files:
            return
            
        latest_file = max(list_of_files, key=os.path.getmtime)
        
        buy_trades, buy_wins, buy_ret = 0, 0, 0.0
        sell_trades, sell_wins, sell_ret = 0, 0, 0.0
        gross_profit, gross_loss = 0.0, 0.0
        
        with open(latest_file, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                signal = row.get("Signal", "")
                win_loss = row.get("Win / Loss", "")
                ret_pct = float(row.get("Return %", 0.0))
                
                if signal == "BUY":
                    buy_trades += 1
                    buy_ret += ret_pct
                    if win_loss == "WIN":
                        buy_wins += 1
                elif signal == "SELL":
                    sell_trades += 1
                    sell_ret += ret_pct
                    if win_loss == "WIN":
                        sell_wins += 1
                        
                if win_loss == "WIN":
                    gross_profit += ret_pct
                elif win_loss == "LOSS":
                    gross_loss += abs(ret_pct)
                    
        total_trades = buy_trades + sell_trades
        total_wins = buy_wins + sell_wins
        total_ret = buy_ret + sell_ret
        
        redirector.metrics["buy_win"] = round((buy_wins / buy_trades * 100) if buy_trades > 0 else 0, 2)
        redirector.metrics["sell_win"] = round((sell_wins / sell_trades * 100) if sell_trades > 0 else 0, 2)
        redirector.metrics["overall_win"] = round((total_wins / total_trades * 100) if total_trades > 0 else 0, 2)
        redirector.metrics["avg_return"] = round((total_ret / total_trades) if total_trades > 0 else 0, 2)
        redirector.metrics["profit_factor"] = round((gross_profit / gross_loss) if gross_loss > 0 else 999.0, 2)

