import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.trade_journal_analytics import TradeJournalAnalytics

class PerformanceDashboard:
    def __init__(self, db_path="data/trade_journal.db", output_dir="reports"):
        self.analytics = TradeJournalAnalytics(db_path)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _generate_report(self, start_date, end_date, title, filename):
        df = self.analytics._fetch_closed_trades(start_date, end_date)
        core = self.analytics.calculate_core_metrics(df)
        sectors = self.analytics.calculate_sector_analytics(df)
        engines = self.analytics.calculate_engine_analytics(df)
        
        md = []
        md.append(f"# {title}")
        md.append(f"Period: {start_date} to {end_date}")
        md.append("")
        
        if df.empty:
            md.append("No completed trades found for this period.")
            report_path = os.path.join(self.output_dir, filename)
            with open(report_path, "w") as f:
                f.write("\n".join(md))
            return report_path
            
        md.append("## Core Performance Metrics")
        md.append(f"- **Total Trades:** {core['total_trades']}")
        md.append(f"- **Win Rate:** {core['win_rate']}%")
        md.append(f"- **Profit Factor:** {core['profit_factor']}")
        md.append(f"- **Expectancy:** {core['expectancy']} per trade")
        md.append(f"- **Max Drawdown:** {core['drawdown']}")
        md.append(f"- **Total PnL:** {core['total_pnl']}")
        md.append("")
        
        md.append("## Trade Execution Stats")
        md.append(f"- **Average Holding Time:** {core['avg_holding_time_mins']} mins")
        md.append(f"- **Average Risk:Reward:** {core['avg_rr']}")
        md.append(f"- **Trade Distribution:** {core['long_trades']} Longs / {core['short_trades']} Shorts")
        md.append("")
        
        md.append("## Engine Analytics")
        md.append(f"- **High Confidence (>80%) Win Rate:** {engines.get('high_confidence_wr', 0.0)}%")
        md.append(f"- **Low Confidence (<80%) Win Rate:** {engines.get('low_confidence_wr', 0.0)}%")
        md.append(f"- **Elite Selection (TQI >85) Win Rate:** {engines.get('elite_tqi_wr', 0.0)}%")
        md.append("")
        
        md.append("## Symbol/Sector Analytics")
        md.append("| Symbol | Trades | Win Rate | PnL |")
        md.append("|---|---|---|---|")
        for sym, data in sorted(sectors.items(), key=lambda x: x[1]['pnl'], reverse=True):
            md.append(f"| {sym} | {data['trades']} | {data['win_rate']:.1f}% | {data['pnl']:.2f} |")
            
        md.append("")
        md.append("## Trade Journal (Recent 10 Trades)")
        md.append("| Date | Symbol | Signal | Entry | Exit | RR | PnL | Exit Reason | Market Regime |")
        md.append("|---|---|---|---|---|---|---|---|---|")
        
        recent = df.sort_values('exit_time', ascending=False).head(10)
        for _, row in recent.iterrows():
            date_str = row['exit_time'].strftime("%Y-%m-%d %H:%M")
            regime = row.get('market_regime', 'Unknown')
            md.append(f"| {date_str} | {row['symbol']} | {row['signal']} | {row['entry_price']} | {row['exit_price']} | {row['rr']} | {row['pnl']:.2f} | {row['exit_reason']} | {regime} |")
            
        report_path = os.path.join(self.output_dir, filename)
        with open(report_path, "w") as f:
            f.write("\n".join(md))
            
        return report_path
        
    def generate_daily_report(self):
        end = datetime.now()
        start = end.replace(hour=0, minute=0, second=0, microsecond=0)
        return self._generate_report(
            start.strftime("%Y-%m-%d %H:%M:%S"), 
            end.strftime("%Y-%m-%d %H:%M:%S"), 
            "Daily Performance Report", 
            "daily_report.md"
        )
        
    def generate_weekly_report(self):
        end = datetime.now()
        start = end - timedelta(days=7)
        return self._generate_report(
            start.strftime("%Y-%m-%d %H:%M:%S"), 
            end.strftime("%Y-%m-%d %H:%M:%S"), 
            "Weekly Performance Report", 
            "weekly_report.md"
        )
        
    def generate_monthly_report(self):
        end = datetime.now()
        start = end - timedelta(days=30)
        return self._generate_report(
            start.strftime("%Y-%m-%d %H:%M:%S"), 
            end.strftime("%Y-%m-%d %H:%M:%S"), 
            "Monthly Performance Report", 
            "monthly_report.md"
        )
        
    def generate_yearly_report(self):
        end = datetime.now()
        start = end - timedelta(days=365)
        return self._generate_report(
            start.strftime("%Y-%m-%d %H:%M:%S"), 
            end.strftime("%Y-%m-%d %H:%M:%S"), 
            "Yearly Performance Report", 
            "yearly_report.md"
        )
