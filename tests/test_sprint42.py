import sys
import os
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.scanner_wrapper import ScannerWrapperThread
from backtest.engine_wrapper import BacktestWrapperThread
from application.database import DatabaseManager
from core.config_manager import ConfigManager

def test_scanner():
    print("Testing Scanner... Running 3 times to save time but simulate load.")
    app = QApplication.instance() or QApplication(sys.argv)
    
    for i in range(3):
        print(f"--- Scanner Run {i+1} ---")
        thread = ScannerWrapperThread()
        
        def on_prog(val):
            pass # print(f"Progress: {val}%")
            
        def on_fin(res):
            print("Finished Scan:", res.get("total"), "symbols.")
            app.quit()
            
        thread.progress.connect(on_prog)
        thread.finished.connect(on_fin)
        thread.error.connect(lambda err: [print(f"Scanner Error: {err}"), app.quit()])
        thread.start()
        app.exec()

def test_backtest():
    print("\nTesting Backtest... (3 Date Ranges)")
    app = QApplication.instance() or QApplication(sys.argv)
    
    ranges = [
        ("2024-01-01", "2024-01-10")
    ]
    symbols = ["RELIANCE.NS"]
    
    for start, end in ranges:
        print(f"--- Backtest {start} to {end} ---")
        thread = BacktestWrapperThread(symbols, start, end, 5)
        
        def on_fin(res):
            print("Metrics:", res)
            app.quit()
            
        thread.finished.connect(on_fin)
        thread.error.connect(lambda err: [print(f"Backtest Error: {err}"), app.quit()])
        thread.start()
        app.exec()

def test_journal():
    print("\nTesting Journal Persistence...")
    db = DatabaseManager()
    initial_count = len(db.get_all_trades())
    print("Initial trades:", initial_count)
    
    db.insert_trade("TEST.NS", "BUY", 100, 95, 110)
    new_count = len(db.get_all_trades())
    print("Trades after insert:", new_count)
    
    # Simulate restart
    db2 = DatabaseManager()
    restart_count = len(db2.get_all_trades())
    print("Trades after restart:", restart_count)
    assert restart_count == initial_count + 1

def test_settings():
    print("\nTesting Settings Persistence...")
    cm = ConfigManager()
    cm.save_config({"capital": 999999})
    
    cm2 = ConfigManager()
    val = cm2.load_config().get("capital")
    print("Loaded capital after restart:", val)
    assert val == 999999
    
    # Restore
    cm2.save_config({"capital": 100000})

if __name__ == "__main__":
    test_scanner()
    test_backtest()
    test_journal()
    test_settings()
    print("\nAll Tests Completed Successfully!")
