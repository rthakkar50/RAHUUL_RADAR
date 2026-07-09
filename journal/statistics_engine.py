from typing import List
from .models import TradeEntry, JournalStats

class StatisticsEngine:
    @staticmethod
    def calculate_stats(trades: List[TradeEntry]) -> JournalStats:
        total_trades = len(trades)
        if total_trades == 0:
            return JournalStats(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
            
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        
        win_rate = (win_count / total_trades) * 100
        
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')
        
        net_pnl = gross_profit - gross_loss
        
        total_rr = sum(t.realized_rr for t in trades)
        avg_rr = total_rr / total_trades
        
        # Max Drawdown Calculation
        peak = 0.0
        current_equity = 0.0
        max_dd = 0.0
        
        for trade in trades:
            current_equity += trade.pnl
            if current_equity > peak:
                peak = current_equity
            
            drawdown = peak - current_equity
            if drawdown > max_dd:
                max_dd = drawdown
                
        return JournalStats(
            total_trades=total_trades,
            winning_trades=win_count,
            losing_trades=loss_count,
            win_rate=round(win_rate, 2),
            average_rr=round(avg_rr, 2),
            max_drawdown=round(max_dd, 2),
            profit_factor=round(profit_factor, 2),
            net_pnl=round(net_pnl, 2)
        )
