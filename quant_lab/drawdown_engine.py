"""
RAHUUL RADAR — Quant Research Lab: Drawdown Engine (Task 3)
===========================================================
Calculates Maximum Drawdown, Current Drawdown, Recovery Time (days),
Longest Losing Streak, Largest Winner, and Largest Loser.
"""

import numpy as np
from typing import List, Dict, Any
from quant_lab.quant_models import DrawdownMetrics


class DrawdownEngine:
    """
    Drawdown & Risk Duration Analyzer.
    """

    def calculate_drawdown_metrics(
        self,
        trade_pnls: List[float],
        initial_capital: float = 1000000.0
    ) -> DrawdownMetrics:
        """Calculates drawdown metrics and streak statistics."""
        if not trade_pnls:
            return DrawdownMetrics(
                max_drawdown_pct=0.0,
                current_drawdown_pct=0.0,
                recovery_time_days=0,
                longest_losing_streak=0,
                largest_winner=0.0,
                largest_loser=0.0
            )

        arr = np.array(trade_pnls)
        equity = np.cumsum(arr) + initial_capital
        peaks = np.maximum.accumulate(equity)

        drawdowns = (peaks - equity) / peaks * 100.0
        max_dd_pct = round(float(np.max(drawdowns)), 2) if len(drawdowns) > 0 else 0.0
        curr_dd_pct = round(float(drawdowns[-1]), 2) if len(drawdowns) > 0 else 0.0

        # Longest Losing Streak & Recovery Time
        longest_losing_streak = 0
        curr_streak = 0
        recovery_days = 0
        current_recovery = 0

        for pnl in trade_pnls:
            if pnl < 0:
                curr_streak += 1
                current_recovery += 1
                if curr_streak > longest_losing_streak:
                    longest_losing_streak = curr_streak
            else:
                curr_streak = 0
                if current_recovery > recovery_days:
                    recovery_days = current_recovery
                current_recovery = 0

        largest_winner = round(float(np.max(arr)), 2) if len(arr) > 0 else 0.0
        largest_loser = round(float(np.min(arr)), 2) if len(arr) > 0 else 0.0

        return DrawdownMetrics(
            max_drawdown_pct=max_dd_pct,
            current_drawdown_pct=curr_dd_pct,
            recovery_time_days=recovery_days,
            longest_losing_streak=longest_losing_streak,
            largest_winner=largest_winner,
            largest_loser=largest_loser
        )
