import logging
import sqlite3
import pandas as pd
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PaperTradingValidationEngine:
    """
    MASTER-11: PAPER TRADING VALIDATION ENGINE (PTVE) V2.0
    Validates Active Trading AI performance before live deployment.
    """
    
    def __init__(self, db_path="data/trade_journal.db"):
        self.db_path = db_path
        self.min_win_rate = 55.0
        self.min_profit_factor = 1.3
        self.max_drawdown = 5.0
        
    def generate_certification_report(self) -> Dict[str, Any]:
        """
        Pulls all trades from the trade_journal.db, computes metrics,
        and returns the certification status.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql("SELECT * FROM trades WHERE status NOT IN ('Waiting', 'Triggered', 'Running')", conn)
            conn.close()
        except Exception as e:
            logger.error(f"[PTVE] Failed to load trade journal: {e}")
            df = pd.DataFrame()
            
        if df.empty:
            return self._empty_report()
            
        # Ensure correct types
        df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce').fillna(0)
        df['pnl_percent'] = pd.to_numeric(df['pnl_percent'], errors='coerce').fillna(0)
        
        total_trades = len(df)
        wins = df[df['pnl'] > 0]
        losses = df[df['pnl'] < 0]
        breakevens = df[df['pnl'] == 0]
        
        win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
        
        gross_profit = wins['pnl'].sum() if not wins.empty else 0
        gross_loss = abs(losses['pnl'].sum()) if not losses.empty else 0
        
        profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else (99.9 if gross_profit > 0 else 0)
        
        avg_win = wins['pnl'].mean() if not wins.empty else 0
        avg_loss = abs(losses['pnl'].mean()) if not losses.empty else 0
        
        expectancy = (win_rate/100 * avg_win) - ((1 - win_rate/100) * avg_loss)
        
        # Max Drawdown Calculation
        df['cum_pnl'] = df['pnl'].cumsum()
        df['peak'] = df['cum_pnl'].cummax()
        df['drawdown'] = df['peak'] - df['cum_pnl']
        max_drawdown = df['drawdown'].max()
        
        # Certification Logic
        certified = False
        if win_rate >= self.min_win_rate and profit_factor >= self.min_profit_factor:
            certified = True
            
        return {
            "status": "READY FOR LIVE DEPLOYMENT" if certified else "NOT READY FOR LIVE TRADING",
            "certified": certified,
            "total_trades": total_trades,
            "wins": len(wins),
            "losses": len(losses),
            "breakevens": len(breakevens),
            "win_rate": round(win_rate, 2),
            "profit_factor": profit_factor,
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "expectancy": round(expectancy, 2),
            "max_drawdown": round(max_drawdown, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2)
        }
        
    def _empty_report(self) -> Dict[str, Any]:
        return {
            "status": "INSUFFICIENT DATA",
            "certified": False,
            "total_trades": 0, "wins": 0, "losses": 0, "breakevens": 0,
            "win_rate": 0.0, "profit_factor": 0.0, "avg_win": 0.0, "avg_loss": 0.0,
            "expectancy": 0.0, "max_drawdown": 0.0,
            "gross_profit": 0.0, "gross_loss": 0.0
        }
