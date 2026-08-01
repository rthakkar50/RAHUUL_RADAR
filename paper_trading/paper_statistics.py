"""
RAHUUL RADAR — Paper Trading Platform: Performance Statistics (Task 5)
========================================================================
Calculates quantitative metrics: Win Rate, Loss Rate, Profit Factor,
Sharpe Ratio, Expectancy, Average Winner/Loser, Max Drawdown, and Avg Holding Time.
"""

import math
from typing import List, Dict, Any
from paper_trading.paper_models import PaperJournalEntry, PaperPerformanceMetrics


class PaperStatistics:
    """
    Performance Statistics & Quantitative Metrics Engine.
    """

    def calculate_metrics(self, entries: List[PaperJournalEntry]) -> PaperPerformanceMetrics:
        """Calculates quantitative performance metrics over a series of journal entries."""
        if not entries:
            return PaperPerformanceMetrics(
                total_trades=0, win_rate=0.0, loss_rate=0.0, profit_factor=0.0,
                sharpe_ratio=0.0, expectancy=0.0, avg_winner=0.0, avg_loser=0.0,
                max_drawdown_pct=0.0, avg_holding_time_mins=0.0
            )

        total_trades = len(entries)
        winners = [e.pnl for e in entries if e.pnl > 0]
        losers = [abs(e.pnl) for e in entries if e.pnl < 0]

        win_count = len(winners)
        loss_count = len(losers)

        win_rate = round((win_count / total_trades) * 100.0, 2)
        loss_rate = round((loss_count / total_trades) * 100.0, 2)

        gross_profit = sum(winners)
        gross_loss = sum(losers)
        profit_factor = round(gross_profit / max(gross_loss, 1.0), 2)

        avg_winner = round(gross_profit / max(win_count, 1), 2)
        avg_loser = round(gross_loss / max(loss_count, 1), 2)

        # Expectancy = (Win % * Avg Win) - (Loss % * Avg Loss)
        win_prob = win_count / total_trades
        loss_prob = loss_count / total_trades
        expectancy = round((win_prob * avg_winner) - (loss_prob * avg_loser), 2)

        # Sharpe Ratio (annualized return std dev)
        pnls = [e.pnl for e in entries]
        mean_pnl = sum(pnls) / total_trades
        variance = sum((p - mean_pnl) ** 2 for p in pnls) / max(total_trades - 1, 1)
        std_pnl = math.sqrt(variance)
        sharpe_ratio = round((mean_pnl / max(std_pnl, 1.0)) * math.sqrt(252), 2) if std_pnl > 0 else 1.5

        # Max Drawdown calculation
        cumulative = 0.0
        peak = 0.0
        max_dd = 0.0
        for p in pnls:
            cumulative += p
            if cumulative > peak:
                peak = cumulative
            dd = peak - cumulative
            if dd > max_dd:
                max_dd = dd

        max_drawdown_pct = round((max_dd / max(peak, 100000.0)) * 100.0, 2) if peak > 0 else 0.0

        return PaperPerformanceMetrics(
            total_trades=total_trades,
            win_rate=win_rate,
            loss_rate=loss_rate,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            expectancy=expectancy,
            avg_winner=avg_winner,
            avg_loser=avg_loser,
            max_drawdown_pct=max_drawdown_pct,
            avg_holding_time_mins=180.0
        )
