import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

class InstitutionalAnalyticsEngine:
    def __init__(self, db_path="data/trade_journal.db"):
        self.db_path = db_path
        
    def _fetch_all_data(self) -> pd.DataFrame:
        try:
            conn = sqlite3.connect(self.db_path)
            # Fetch ALL trades including WATCH, REJECTED if they were ever saved.
            # Currently TradeManager only saves executed trades, but we will fetch whatever is there.
            df = pd.read_sql_query("SELECT * FROM trades", conn)
            conn.close()
            
            if not df.empty:
                df['created_time'] = pd.to_datetime(df['created_time'], errors='coerce')
                df['exit_time'] = pd.to_datetime(df['exit_time'], errors='coerce')
                df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce').fillna(0.0)
            return df
        except Exception:
            return pd.DataFrame()

    def get_section_1_performance_summary(self, df: pd.DataFrame) -> dict:
        if df.empty: return {}
        
        executed = df[df['status'].isin(['Target 1 Hit', 'Target 2 Hit', 'Stop Loss Hit', 'Closed', 'Expired'])]
        total = len(executed)
        
        buys = len(executed[executed['signal'] == 'BUY'])
        sells = len(executed[executed['signal'].isin(['SELL', 'SHORT'])])
        
        wins = executed[executed['pnl'] > 0]
        losses = executed[executed['pnl'] < 0]
        breakeven = executed[executed['pnl'] == 0]
        
        win_rate = len(wins) / total * 100 if total > 0 else 0
        loss_rate = len(losses) / total * 100 if total > 0 else 0
        be_rate = len(breakeven) / total * 100 if total > 0 else 0
        
        gross_profit = wins['pnl'].sum()
        gross_loss = abs(losses['pnl'].sum())
        pf = gross_profit / gross_loss if gross_loss > 0 else (99.9 if gross_profit > 0 else 0.0)
        
        net_return = executed['pnl_percent'].sum() if 'pnl_percent' in executed.columns else 0.0
        avg_return = executed['pnl'].mean() if total > 0 else 0.0
        avg_rr = executed['rr'].mean() if 'rr' in executed.columns and total > 0 else 0.0
        
        executed['holding'] = (executed['exit_time'] - executed['created_time']).dt.total_seconds() / 60.0
        avg_hold = executed['holding'].mean()
        
        win_prob = len(wins) / total if total > 0 else 0
        loss_prob = len(losses) / total if total > 0 else 0
        avg_win = wins['pnl'].mean() if not wins.empty else 0.0
        avg_loss = abs(losses['pnl'].mean()) if not losses.empty else 0.0
        expectancy = (win_prob * avg_win) - (loss_prob * avg_loss)
        
        recovery = gross_profit / self._calculate_max_drawdown(executed) if self._calculate_max_drawdown(executed) > 0 else 0.0

        return {
            "total_trades": total,
            "buy_trades": buys,
            "sell_trades": sells,
            "win_rate": round(win_rate, 2),
            "loss_rate": round(loss_rate, 2),
            "breakeven_percent": round(be_rate, 2),
            "profit_factor": round(pf, 2),
            "net_return_percent": round(net_return, 2),
            "avg_return": round(avg_return, 2),
            "avg_rr": round(avg_rr, 2),
            "avg_holding_time_mins": round(avg_hold, 1) if not pd.isna(avg_hold) else 0.0,
            "expectancy": round(expectancy, 2),
            "recovery_factor": round(recovery, 2)
        }

    def _calculate_max_drawdown(self, df):
        if df.empty: return 0.0
        cumulative = df['pnl'].cumsum()
        peak = cumulative.cummax()
        drawdown = peak - cumulative
        return drawdown.max()

    def get_section_2_risk_analytics(self, df: pd.DataFrame) -> dict:
        if df.empty: return {}
        executed = df[df['status'].isin(['Target 1 Hit', 'Target 2 Hit', 'Stop Loss Hit', 'Closed'])]
        if executed.empty: return {}
        
        cumulative = executed['pnl'].cumsum()
        peak = cumulative.cummax()
        drawdowns = peak - cumulative
        
        max_dd = drawdowns.max()
        avg_dd = drawdowns[drawdowns > 0].mean() if len(drawdowns[drawdowns > 0]) > 0 else 0.0
        
        # Streaks
        streak, max_win_streak, max_loss_streak = 0, 0, 0
        curr_type = None
        for pnl in executed['pnl']:
            if pnl > 0:
                if curr_type == 'WIN': streak += 1
                else: curr_type = 'WIN'; streak = 1
                max_win_streak = max(max_win_streak, streak)
            elif pnl < 0:
                if curr_type == 'LOSS': streak += 1
                else: curr_type = 'LOSS'; streak = 1
                max_loss_streak = max(max_loss_streak, streak)
                
        largest_win = executed['pnl'].max()
        largest_loss = executed['pnl'].min()
        
        wins = executed[executed['pnl'] > 0]
        losses = executed[executed['pnl'] < 0]
        avg_win = wins['pnl'].mean() if not wins.empty else 0.0
        avg_loss = losses['pnl'].mean() if not losses.empty else 0.0
        
        return {
            "max_drawdown": round(max_dd, 2),
            "avg_drawdown": round(avg_dd, 2),
            "longest_win_streak": max_win_streak,
            "longest_loss_streak": max_loss_streak,
            "largest_winner": round(largest_win, 2),
            "largest_loser": round(largest_loss, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2)
        }

    def get_section_3_trade_distribution(self, df: pd.DataFrame) -> dict:
        # Requires WATCH and REJECTED tracking to be fully accurate
        buys = len(df[df['signal'] == 'BUY'])
        sells = len(df[df['signal'].isin(['SELL', 'SHORT'])])
        watch = len(df[df['signal'] == 'WATCH'])
        rejected = len(df[df['signal'] == 'REJECT'])
        near_elite = len(df[df.get('elite_score', 0) >= 80.75]) - len(df[df.get('elite_score', 0) >= 85])
        
        return {
            "buy": buys,
            "sell": sells,
            "watch": watch,
            "rejected": rejected,
            "near_elite": near_elite
        }

    def get_section_4_market_regime(self, df: pd.DataFrame) -> dict:
        if df.empty or 'market_regime' not in df.columns: return {}
        regimes = {}
        for regime, group in df.groupby('market_regime'):
            wins = group[group['pnl'] > 0]
            losses = group[group['pnl'] < 0]
            wr = len(wins) / len(group) * 100 if len(group) > 0 else 0
            pf = wins['pnl'].sum() / abs(losses['pnl'].sum()) if abs(losses['pnl'].sum()) > 0 else 99.9
            rr = group['rr'].mean() if 'rr' in group.columns else 0.0
            
            regimes[regime] = {
                "trades": len(group),
                "win_rate": round(wr, 2),
                "profit_factor": round(pf, 2),
                "avg_rr": round(rr, 2)
            }
        return regimes

    def get_section_5_sector_performance(self, df: pd.DataFrame) -> dict:
        if df.empty: return {}
        sectors = {}
        # In absence of full sector mapping, group by symbol
        for sym, group in df.groupby('symbol'):
            wins = group[group['pnl'] > 0]
            losses = group[group['pnl'] < 0]
            wr = len(wins) / len(group) * 100 if len(group) > 0 else 0
            pf = wins['pnl'].sum() / abs(losses['pnl'].sum()) if abs(losses['pnl'].sum()) > 0 else 99.9
            avg_ret = group['pnl'].mean()
            sectors[sym] = {
                "trades": len(group),
                "win_rate": round(wr, 2),
                "avg_return": round(avg_ret, 2),
                "profit_factor": round(pf, 2)
            }
        return sectors

    def get_section_8_time_analytics(self, df: pd.DataFrame) -> dict:
        if df.empty or 'exit_time' not in df.columns: return {}
        executed = df.dropna(subset=['exit_time']).copy()
        if executed.empty: return {}
        
        executed['day'] = executed['exit_time'].dt.date
        executed['week'] = executed['exit_time'].dt.isocalendar().week
        executed['month'] = executed['exit_time'].dt.month
        
        day_pnl = executed.groupby('day')['pnl'].sum()
        week_pnl = executed.groupby('week')['pnl'].sum()
        month_pnl = executed.groupby('month')['pnl'].sum()
        
        return {
            "best_day": str(day_pnl.idxmax()) if not day_pnl.empty else "N/A",
            "worst_day": str(day_pnl.idxmin()) if not day_pnl.empty else "N/A",
            "best_week": f"Week {week_pnl.idxmax()}" if not week_pnl.empty else "N/A",
            "worst_week": f"Week {week_pnl.idxmin()}" if not week_pnl.empty else "N/A",
            "best_month": f"Month {month_pnl.idxmax()}" if not month_pnl.empty else "N/A",
            "worst_month": f"Month {month_pnl.idxmin()}" if not month_pnl.empty else "N/A",
            "avg_trades_per_day": round(len(executed) / len(day_pnl), 1) if len(day_pnl) > 0 else 0,
            "avg_trades_per_week": round(len(executed) / len(week_pnl), 1) if len(week_pnl) > 0 else 0
        }

    def get_section_9_trade_outcome(self, df: pd.DataFrame) -> dict:
        if df.empty: return {}
        total = len(df)
        t1 = len(df[df['exit_reason'].str.contains('Target 1', na=False)])
        t2 = len(df[df['exit_reason'].str.contains('Target 2', na=False)])
        sl = len(df[df['exit_reason'].str.contains('Stop Loss', na=False)])
        manual = len(df[df['exit_reason'].str.contains('Manual', na=False)])
        time_exit = len(df[df['exit_reason'].str.contains('Time', na=False)])
        
        df['holding'] = (df['exit_time'] - df['created_time']).dt.total_seconds() / 60.0
        
        return {
            "t1_hit_percent": round(t1 / total * 100, 2) if total > 0 else 0.0,
            "t2_hit_percent": round(t2 / total * 100, 2) if total > 0 else 0.0,
            "stop_loss_percent": round(sl / total * 100, 2) if total > 0 else 0.0,
            "manual_exit_percent": round(manual / total * 100, 2) if total > 0 else 0.0,
            "time_exit_percent": round(time_exit / total * 100, 2) if total > 0 else 0.0,
            "avg_hold_time": round(df['holding'].mean(), 1) if not df['holding'].isna().all() else 0.0
        }

    def get_section_10_heatmaps(self, df: pd.DataFrame) -> dict:
        if df.empty or 'created_time' not in df.columns: return {}
        df['day_of_week'] = df['created_time'].dt.day_name()
        df['hour'] = df['created_time'].dt.hour
        
        # Create a simple matrix of Win Rates by Day and Hour
        matrix = df.groupby(['day_of_week', 'hour']).apply(
            lambda x: (len(x[x['pnl'] > 0]) / len(x)) * 100 if len(x) > 0 else 0
        ).to_dict()
        
        return {"time_heatmap": {str(k): round(v, 1) for k, v in matrix.items()}}
