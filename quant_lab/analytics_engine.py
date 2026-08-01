"""
RAHUUL RADAR — Quant Research Lab: Strategy Analytics Engine (Task 1)
=====================================================================
Calculates quantitative metrics: Win Rate, Loss Rate, Profit Factor, Expectancy,
Average Winner/Loser, Risk-to-Reward Ratio, Recovery Factor, and Ulcer Index.
"""

import math
import numpy as np
from typing import List, Dict, Any
from quant_lab.quant_models import StrategyAnalytics


class StrategyAnalyticsEngine:
    """
    Statistical Analytics & Quantitative Discovery Engine.
    """

    def analyze_trades(self, trade_pnls: List[float], initial_capital: float = 1000000.0) -> StrategyAnalytics:
        """Calculates Strategy Analytics metrics over a vector of trade PnLs."""
        if not trade_pnls:
            return StrategyAnalytics(
                total_trades=0, win_rate=0.0, loss_rate=0.0, profit_factor=0.0,
                expectancy=0.0, avg_winner=0.0, avg_loser=0.0, risk_reward=0.0,
                recovery_factor=0.0, ulcer_index=0.0
            )

        total_trades = len(trade_pnls)
        arr = np.array(trade_pnls)

        winners = arr[arr > 0]
        losers = np.abs(arr[arr < 0])

        win_count = len(winners)
        loss_count = len(losers)

        win_rate = round((win_count / total_trades) * 100.0, 2)
        loss_rate = round((loss_count / total_trades) * 100.0, 2)

        gross_profit = float(np.sum(winners)) if win_count > 0 else 0.0
        gross_loss = float(np.sum(losers)) if loss_count > 0 else 0.0

        profit_factor = round(gross_profit / max(gross_loss, 1.0), 2)
        avg_winner = round(gross_profit / max(win_count, 1), 2)
        avg_loser = round(gross_loss / max(loss_count, 1), 2)

        win_prob = win_count / total_trades
        loss_prob = loss_count / total_trades
        expectancy = round((win_prob * avg_winner) - (loss_prob * avg_loser), 2)

        risk_reward = round(avg_winner / max(avg_loser, 1.0), 2)

        # Recovery Factor = Total Net Profit / Max Drawdown Amount
        net_profit = gross_profit - gross_loss
        cum_equity = np.cumsum(arr) + initial_capital
        peak = np.maximum.accumulate(cum_equity)
        drawdowns = peak - cum_equity
        max_dd = float(np.max(drawdowns)) if len(drawdowns) > 0 else 1.0
        recovery_factor = round(net_profit / max(max_dd, 1.0), 2)

        # Ulcer Index = Sqrt( Mean( (Drawdown_Pct)^2 ) )
        dd_pct = (drawdowns / peak) * 100.0 if len(peak) > 0 else np.zeros_like(arr)
        ulcer_index = round(float(np.sqrt(np.mean(dd_pct ** 2))), 2) if len(dd_pct) > 0 else 0.0

        return StrategyAnalytics(
            total_trades=total_trades,
            win_rate=win_rate,
            loss_rate=loss_rate,
            profit_factor=profit_factor,
            expectancy=expectancy,
            avg_winner=avg_winner,
            avg_loser=avg_loser,
            risk_reward=risk_reward,
            recovery_factor=recovery_factor,
            ulcer_index=ulcer_index
        )
