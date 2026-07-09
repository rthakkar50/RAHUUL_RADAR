import os
import sys
import json
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.institutional_analytics_engine import InstitutionalAnalyticsEngine

class InstitutionalDashboardService:
    def __init__(self, db_path="data/trade_journal.db", output_dir="reports/analytics"):
        self.engine = InstitutionalAnalyticsEngine(db_path)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_full_dashboard(self):
        df = self.engine._fetch_all_data()
        
        # 1. Gather all analytical blocks
        s1 = self.engine.get_section_1_performance_summary(df)
        s2 = self.engine.get_section_2_risk_analytics(df)
        s3 = self.engine.get_section_3_trade_distribution(df)
        s4 = self.engine.get_section_4_market_regime(df)
        s5 = self.engine.get_section_5_sector_performance(df)
        s8 = self.engine.get_section_8_time_analytics(df)
        s9 = self.engine.get_section_9_trade_outcome(df)
        s10 = self.engine.get_section_10_heatmaps(df)
        
        # Dummy stubs for Sections 6 and 7 until XAI logs are natively persisted
        s6_engine = {
            "Trend Engine": {"Contribution": "25%", "Accuracy": "65%", "Pass": "80%", "Reject": "20%"},
            "Momentum Engine": {"Contribution": "20%", "Accuracy": "55%", "Pass": "70%", "Reject": "30%"}
        }
        s7_xai = {
            "most_common_rejection": "Only two engines agree",
            "near_elite_frequency": s3.get('near_elite', 0),
            "critical_failures": "Elite Selection (TQI < 85)",
            "frequent_recommendation": "Monitor next candle."
        }
        
        snapshot = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "section_1_performance": s1,
            "section_2_risk": s2,
            "section_3_distribution": s3,
            "section_4_regime": s4,
            "section_5_sector": s5,
            "section_6_engines": s6_engine,
            "section_7_xai": s7_xai,
            "section_8_time": s8,
            "section_9_outcomes": s9,
            "section_10_heatmaps": s10
        }
        
        self._export_json(snapshot)
        self._export_csv(df)
        self._export_markdown(snapshot)
        
        return os.path.join(self.output_dir, "dashboard_snapshot.md")

    def _export_json(self, data):
        with open(os.path.join(self.output_dir, "analytics_snapshot.json"), "w") as f:
            json.dump(data, f, indent=4)
            
    def _export_csv(self, df):
        if not df.empty:
            df.to_csv(os.path.join(self.output_dir, "analytics_export.csv"), index=False)
            
    def _export_markdown(self, data):
        md = []
        md.append("# INSTITUTIONAL RISK ANALYTICS & PERFORMANCE DASHBOARD")
        md.append(f"Generated: {data['timestamp']}\n")
        
        # SECTION 1
        md.append("## SECTION-1: PERFORMANCE SUMMARY")
        s1 = data['section_1_performance']
        if not s1:
            md.append("No data available.")
        else:
            md.append(f"- **Total Trades:** {s1.get('total_trades')}")
            md.append(f"- **BUY Trades:** {s1.get('buy_trades')} | **SELL Trades:** {s1.get('sell_trades')}")
            md.append(f"- **Win Rate:** {s1.get('win_rate')}% | **Loss Rate:** {s1.get('loss_rate')}% | **Breakeven:** {s1.get('breakeven_percent')}%")
            md.append(f"- **Profit Factor:** {s1.get('profit_factor')}")
            md.append(f"- **Net Return:** {s1.get('net_return_percent')}%")
            md.append(f"- **Average Return:** {s1.get('avg_return')}")
            md.append(f"- **Average RR:** {s1.get('avg_rr')}")
            md.append(f"- **Average Holding Time:** {s1.get('avg_holding_time_mins')} mins")
            md.append(f"- **Expectancy:** {s1.get('expectancy')}")
            md.append(f"- **Recovery Factor:** {s1.get('recovery_factor')}\n")
            
        # SECTION 2
        md.append("## SECTION-2: RISK ANALYTICS")
        s2 = data['section_2_risk']
        if s2:
            md.append(f"- **Maximum Drawdown:** {s2.get('max_drawdown')}")
            md.append(f"- **Average Drawdown:** {s2.get('avg_drawdown')}")
            md.append(f"- **Longest Win Streak:** {s2.get('longest_win_streak')} | **Longest Loss Streak:** {s2.get('longest_loss_streak')}")
            md.append(f"- **Largest Winner:** {s2.get('largest_winner')} | **Largest Loser:** {s2.get('largest_loser')}")
            md.append(f"- **Average Win:** {s2.get('avg_win')} | **Average Loss:** {s2.get('avg_loss')}\n")
            
        # SECTION 3
        md.append("## SECTION-3: TRADE DISTRIBUTION")
        s3 = data['section_3_distribution']
        if s3:
            md.append(f"- **BUY:** {s3.get('buy')}")
            md.append(f"- **SELL:** {s3.get('sell')}")
            md.append(f"- **WATCH:** {s3.get('watch')}")
            md.append(f"- **REJECTED:** {s3.get('rejected')}")
            md.append(f"- **NEAR ELITE:** {s3.get('near_elite')}\n")
            
        # SECTION 4
        md.append("## SECTION-4: MARKET REGIME ANALYTICS")
        s4 = data['section_4_regime']
        if s4:
            md.append("| Regime | Trades | Win Rate | Profit Factor | Avg RR |")
            md.append("|---|---|---|---|---|")
            for r, d in s4.items():
                md.append(f"| {r} | {d['trades']} | {d['win_rate']}% | {d['profit_factor']} | {d['avg_rr']} |")
        md.append("")
        
        # SECTION 5
        md.append("## SECTION-5: SECTOR PERFORMANCE")
        s5 = data['section_5_sector']
        if s5:
            md.append("| Sector/Symbol | Trades | Win Rate | Avg Return | Profit Factor |")
            md.append("|---|---|---|---|---|")
            for sym, d in s5.items():
                md.append(f"| {sym} | {d['trades']} | {d['win_rate']}% | {d['avg_return']} | {d['profit_factor']} |")
        md.append("")
        
        # SECTION 6
        md.append("## SECTION-6: ENGINE PERFORMANCE (Mocked)")
        s6 = data['section_6_engines']
        for k, v in s6.items():
            md.append(f"- **{k}:** Accuracy {v['Accuracy']} (Pass: {v['Pass']}, Reject: {v['Reject']})")
        md.append("")
        
        # SECTION 7
        md.append("## SECTION-7: EXPLAINABLE AI ANALYTICS")
        s7 = data['section_7_xai']
        md.append(f"- **Most Common Rejection:** {s7.get('most_common_rejection')}")
        md.append(f"- **Near Elite Frequency:** {s7.get('near_elite_frequency')}")
        md.append(f"- **Critical Failures:** {s7.get('critical_failures')}")
        md.append(f"- **Most Frequent Recommendation:** {s7.get('frequent_recommendation')}\n")
        
        # SECTION 8
        md.append("## SECTION-8: TIME ANALYTICS")
        s8 = data['section_8_time']
        if s8:
            md.append(f"- **Best / Worst Day:** {s8.get('best_day')} / {s8.get('worst_day')}")
            md.append(f"- **Best / Worst Week:** {s8.get('best_week')} / {s8.get('worst_week')}")
            md.append(f"- **Best / Worst Month:** {s8.get('best_month')} / {s8.get('worst_month')}")
            md.append(f"- **Avg Trades / Day:** {s8.get('avg_trades_per_day')} | **/ Week:** {s8.get('avg_trades_per_week')}\n")
            
        # SECTION 9
        md.append("## SECTION-9: TRADE OUTCOME ANALYTICS")
        s9 = data['section_9_outcomes']
        if s9:
            md.append(f"- **Target 1 Hit:** {s9.get('t1_hit_percent')}%")
            md.append(f"- **Target 2 Hit:** {s9.get('t2_hit_percent')}%")
            md.append(f"- **Stop Loss Hit:** {s9.get('stop_loss_percent')}%")
            md.append(f"- **Manual Exit:** {s9.get('manual_exit_percent')}%")
            md.append(f"- **Time Exit:** {s9.get('time_exit_percent')}%")
            md.append(f"- **Avg Hold Time:** {s9.get('avg_hold_time')} mins\n")
            
        with open(os.path.join(self.output_dir, "dashboard_snapshot.md"), "w") as f:
            f.write("\n".join(md))

if __name__ == "__main__":
    service = InstitutionalDashboardService()
    path = service.generate_full_dashboard()
    print(f"Dashboard generated at {path}")
