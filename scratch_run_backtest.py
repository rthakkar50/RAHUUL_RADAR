import os
import sys
import json
from datetime import datetime, timedelta
sys.path.append(os.path.abspath('.'))

from backtest.engine_wrapper import BacktestWrapperThread

class MockSignal:
    def emit(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], dict):
            print(json.dumps(args[0], indent=2))
        elif args:
            print("SIGNAL:", args)
        
    def connect(self, *args):
        pass

def main():
    symbols = ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "RELIANCE.NS", "INFY.NS", "TCS.NS", "ITC.NS", "LNT.NS", "AXISBANK.NS", "KOTAKBANK.NS"]
    start = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y-%m-%d")
    
    wrapper = BacktestWrapperThread(symbols, start, end, holding_days=10)
    wrapper.progress = MockSignal()
    wrapper.log = MockSignal()
    wrapper.finished = MockSignal()
    wrapper.error = MockSignal()
    
    wrapper.run()
    
    print("BACKTEST FINISHED")

if __name__ == '__main__':
    main()
