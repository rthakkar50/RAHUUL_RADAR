import sqlite3
import pandas as pd
from datetime import datetime, timedelta

class TradeJournalAnalytics:
    def __init__(self, db_path="data/trade_journal.db"):
        self.db_path = db_path
        
    def _fetch_closed_trades(self, start_date=None, end_date=None):
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM trades WHERE status NOT IN ('Waiting', 'Triggered', 'Running')"
        
        # We will filter dates using pandas for simplicity
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return df
            
        df['created_time'] = pd.to_datetime(df['created_time'])
        df['exit_time'] = pd.to_datetime(df['exit_time'])
        
        if start_date:
            df = df[df['created_time'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['created_time'] <= pd.to_datetime(end_date)]
            
        return df

    def calculate_core_metrics(self, df: pd.DataFrame) -> dict:
        if df.empty:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "drawdown": 0.0,
                "expectancy": 0.0,
                "avg_holding_time_mins": 0.0,
                "avg_rr": 0.0,
                "total_pnl": 0.0,
                "long_trades": 0,
                "short_trades": 0
            }
            
        wins = df[df['pnl'] > 0]
        losses = df[df['pnl'] <= 0]
        
        win_rate = (len(wins) / len(df)) * 100 if len(df) > 0 else 0
        
        gross_profit = wins['pnl'].sum() if not wins.empty else 0.0
        gross_loss = abs(losses['pnl'].sum()) if not losses.empty else 0.0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (99.9 if gross_profit > 0 else 0.0)
        
        avg_win = wins['pnl'].mean() if not wins.empty else 0.0
        avg_loss = abs(losses['pnl'].mean()) if not losses.empty else 0.0
        
        win_prob = len(wins) / len(df)
        loss_prob = len(losses) / len(df)
        expectancy = (win_prob * avg_win) - (loss_prob * avg_loss)
        
        # Calculate Max Drawdown based on cumulative PnL
        cumulative = df['pnl'].cumsum()
        peak = cumulative.cummax()
        drawdown = peak - cumulative
        max_drawdown = drawdown.max()
        
        # Holding time
        df['holding_time'] = (df['exit_time'] - df['created_time']).dt.total_seconds() / 60.0
        avg_holding = df['holding_time'].mean()
        
        avg_rr = df['rr'].mean() if 'rr' in df.columns else 0.0
        total_pnl = df['pnl'].sum()
        
        longs = len(df[df['signal'] == 'BUY'])
        shorts = len(df[df['signal'].isin(['SELL', 'SHORT'])])
        
        return {
            "total_trades": len(df),
            "win_rate": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2),
            "drawdown": round(max_drawdown, 2),
            "expectancy": round(expectancy, 2),
            "avg_holding_time_mins": round(avg_holding, 1),
            "avg_rr": round(avg_rr, 2),
            "total_pnl": round(total_pnl, 2),
            "long_trades": longs,
            "short_trades": shorts
        }
        
    def calculate_sector_analytics(self, df: pd.DataFrame) -> dict:
        if df.empty:
            return {}
            
        # Simplified: group by symbol prefix for sector if real sector isn't in DB
        # Ideally, we map symbols to sectors. Let's just group by symbol for now
        sector_perf = {}
        for symbol, group in df.groupby('symbol'):
            wins = len(group[group['pnl'] > 0])
            wr = (wins / len(group)) * 100
            pnl = group['pnl'].sum()
            sector_perf[symbol] = {"trades": len(group), "win_rate": wr, "pnl": pnl}
            
        return sector_perf
        
    def calculate_engine_analytics(self, df: pd.DataFrame) -> dict:
        if df.empty:
            return {}
            
        # Correlate scores with win rate
        high_conf = df[df['confidence'] >= 80.0]
        low_conf = df[df['confidence'] < 80.0]
        
        high_tqi = df[df['elite_score'] >= 85.0] if 'elite_score' in df.columns else pd.DataFrame()
        
        def safe_wr(subset):
            if subset.empty: return 0.0
            w = len(subset[subset['pnl'] > 0])
            return round((w / len(subset)) * 100, 2)
            
        return {
            "high_confidence_wr": safe_wr(high_conf),
            "low_confidence_wr": safe_wr(low_conf),
            "elite_tqi_wr": safe_wr(high_tqi)
        }
