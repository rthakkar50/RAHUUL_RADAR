"""
RAHUUL RADAR — Quant Research Lab: Equity Curve Engine (Task 2)
==============================================================
Generates Daily, Weekly, and Monthly Equity Curves, Drawdown Curves, and Rolling Win Rate.
"""

import numpy as np
from typing import List, Dict, Any
from quant_lab.quant_models import EquityCurveData


class EquityCurveEngine:
    """
    Equity Curve & Time-Series Performance Generator.
    """

    def generate_equity_curves(
        self,
        trade_pnls: List[float],
        initial_capital: float = 1000000.0,
        rolling_window: int = 20
    ) -> EquityCurveData:
        """Generates daily, weekly, monthly equity curves and rolling win rate."""
        if not trade_pnls:
            return EquityCurveData(
                daily_equity=[initial_capital],
                weekly_equity=[initial_capital],
                monthly_equity=[initial_capital],
                drawdown_curve=[0.0],
                rolling_win_rate=[0.0]
            )

        arr = np.array(trade_pnls)
        daily_equity = (np.cumsum(arr) + initial_capital).tolist()

        # Weekly and Monthly downsampled aggregation
        step_weekly = max(len(daily_equity) // 10, 1)
        step_monthly = max(len(daily_equity) // 4, 1)

        weekly_equity = daily_equity[::step_weekly]
        monthly_equity = daily_equity[::step_monthly]

        # Drawdown curve
        eq_arr = np.array(daily_equity)
        peaks = np.maximum.accumulate(eq_arr)
        drawdown_curve = (((peaks - eq_arr) / peaks) * 100.0).tolist()

        # Rolling win rate
        wins = (arr > 0).astype(float)
        rolling_win_rate = []
        for i in range(len(arr)):
            start_idx = max(0, i - rolling_window + 1)
            window_slice = wins[start_idx:i+1]
            rolling_win_rate.append(round(float(np.mean(window_slice) * 100.0), 2))

        return EquityCurveData(
            daily_equity=[round(e, 2) for e in daily_equity],
            weekly_equity=[round(e, 2) for e in weekly_equity],
            monthly_equity=[round(e, 2) for e in monthly_equity],
            drawdown_curve=[round(d, 2) for d in drawdown_curve],
            rolling_win_rate=rolling_win_rate
        )
