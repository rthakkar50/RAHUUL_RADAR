import os
import csv
from datetime import datetime
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class PerformanceAnalytics:
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def generate_summary(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates and prints statistics for the completed trades.
        Returns a metrics dictionary for UI consumption.
        """
        if not trades:
            logger.warning("No tradable signals found to evaluate.")
            return {}
            
        buy_trades = [t for t in trades if t["Signal"] == "BUY"]
        sell_trades = [t for t in trades if t["Signal"] == "SELL"]
        
        def calculate_metrics(trade_list):
            tot = len(trade_list)
            if tot == 0:
                return 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            
            win = sum(1 for t in trade_list if t["Win / Loss"] == "WIN")
            loss = sum(1 for t in trade_list if t["Win / Loss"] == "LOSS")
            win_rate = (win / tot * 100)
            avg_ret = (sum(t["Return %"] for t in trade_list) / tot)
            
            gross_profit = sum(t["Return %"] for t in trade_list if t["Win / Loss"] == "WIN")
            gross_loss = abs(sum(t["Return %"] for t in trade_list if t["Win / Loss"] == "LOSS"))
            pf = (gross_profit / gross_loss) if gross_loss > 0 else 999.0
            
            max_gain = max([t["Return %"] for t in trade_list] + [0.0])
            max_loss = min([t["Return %"] for t in trade_list] + [0.0])
            avg_hold = sum(t["Holding Days"] for t in trade_list) / tot
            
            return tot, win, loss, win_rate, avg_ret, max_gain, max_loss, pf, avg_hold
            
        tot_all, win_all, loss_all, wr_all, avg_all, mxg_all, mxl_all, pf_all, hold_all = calculate_metrics(trades)
        tot_b, win_b, loss_b, wr_b, avg_b, mxg_b, mxl_b, pf_b, hold_b = calculate_metrics(buy_trades)
        tot_s, win_s, loss_s, wr_s, avg_s, mxg_s, mxl_s, pf_s, hold_s = calculate_metrics(sell_trades)
        
        print("\n======================================================================")
        print("                 INSTITUTIONAL PERFORMANCE SUMMARY")
        print("======================================================================")
        print(f"Total Evaluated Trades: {tot_all}")
        print(f"Overall Win Rate:       {wr_all:.2f}% ({win_all}W / {loss_all}L)")
        print(f"Overall Profit Factor:  {pf_all:.2f}")
        print(f"Average Return / Trade: {avg_all:.2f}%")
        print(f"Average Holding Time:   {hold_all:.1f} days")
        print(f"Maximum Drawdown (1T):  {mxl_all:.2f}%")
        print(f"Best Trade:             +{mxg_all:.2f}%")
        print("----------------------------------------------------------------------")
        print(f"BUY  Win Rate: {wr_b:.2f}%  | Trades: {tot_b} | PF: {pf_b:.2f} | Avg Ret: {avg_b:.2f}%")
        print(f"SELL Win Rate: {wr_s:.2f}%  | Trades: {tot_s} | PF: {pf_s:.2f} | Avg Ret: {avg_s:.2f}%")
        print("======================================================================\n")

        return {
            "buy_win": round(wr_b, 2),
            "sell_win": round(wr_s, 2),
            "overall_win": round(wr_all, 2),
            "profit_factor": round(pf_all, 2),
            "avg_return": round(avg_all, 2)
        }

    def export_to_csv(self, trades: List[Dict[str, Any]]):
        if not trades:
            return
            
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = f"simulated_trades_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        headers = list(trades[0].keys())
        
        try:
            with open(filepath, mode="w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for t in trades:
                    writer.writerow(t)
            logger.info(f"Simulated trades exported to: {filepath}")
        except Exception as e:
            logger.error(f"Failed to export trades CSV: {e}")
