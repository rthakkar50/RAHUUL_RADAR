import os
import sys
import sqlite3
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from application.performance_dashboard import PerformanceDashboard
from application.trade_manager import TradeManager

def populate_dummy_trades():
    # Initialize the DB properly via TradeManager
    tm = TradeManager.get_instance()
    
    conn = sqlite3.connect(tm.db_path)
    c = conn.cursor()
    
    now = datetime.now()
    
    dummy_trades = [
        # Win
        ("test-1", "RELIANCE.NS", "BUY", "5m", "Intraday", 2500.0, 2480.0, 2520.0, 2540.0, 1.5,
         85.0, 88.0, "A", (now - timedelta(days=2, hours=3)).strftime("%Y-%m-%d %H:%M:%S"), "", "Target 2 Hit", 
         2540.0, "Target 2 Hit", (now - timedelta(days=2, hours=1)).strftime("%Y-%m-%d %H:%M:%S"), 40.0, 1.6, "Bullish", 90.0),
        # Loss
        ("test-2", "HDFCBANK.NS", "SELL", "15m", "Intraday", 1600.0, 1620.0, 1580.0, 1560.0, 1.2,
         75.0, 70.0, "B", (now - timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M:%S"), "", "Stop Loss Hit", 
         1620.0, "Stop Loss Hit", (now - timedelta(days=1, hours=3)).strftime("%Y-%m-%d %H:%M:%S"), -20.0, -1.25, "Bearish", 75.0),
        # Win
        ("test-3", "INFY.NS", "BUY", "5m", "Scalp", 1400.0, 1390.0, 1420.0, 1440.0, 2.0,
         89.0, 92.0, "A+", (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"), "", "Target 1 Hit", 
         1420.0, "Target 1 Hit", (now - timedelta(hours=4, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"), 20.0, 1.4, "Bullish", 95.0)
    ]
    
    c.executemany('''
        INSERT OR REPLACE INTO trades (
            id, symbol, signal, timeframe, strategy, entry_price, sl, t1, t2, rr, 
            score, confidence, quality, created_time, expiry_time, status, 
            exit_price, exit_reason, exit_time, pnl, pnl_percent, market_regime, elite_score
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', dummy_trades)
    
    conn.commit()
    conn.close()

def run():
    print("Populating dummy trades for testing...")
    populate_dummy_trades()
    
    print("Generating Performance Dashboard (Weekly Report)...")
    dashboard = PerformanceDashboard(output_dir="/Users/pr/.gemini/antigravity/brain/6fcf3ef8-4bc0-4c18-94e2-4baaf42526ce/")
    report_path = dashboard.generate_weekly_report()
    
    print(f"Report successfully generated at: {report_path}")

if __name__ == "__main__":
    run()
