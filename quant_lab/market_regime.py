"""
RAHUUL RADAR — Quant Research Lab: Market Regime Analytics (Task 6)
===================================================================
Automatically classifies market environments (Bull, Bear, Sideways, High/Low Volatility)
and computes strategy performance metrics broken down by regime.
"""

from typing import List, Dict, Any
from quant_lab.quant_models import RegimePerformance


class MarketRegimeAnalytics:
    """
    Regime-Specific Strategy Performance Analyzer.
    """

    def analyze_regimes(self, trade_records: List[Dict[str, Any]]) -> List[RegimePerformance]:
        """Calculates win rate, profit factor, total PnL, and trade count per market regime."""
        regimes = ["Strong Bull Trend", "Bull Trend", "Bear Trend", "Sideways / Volatile", "Low Volatility"]

        regime_data: Dict[str, List[float]] = {r: [] for r in regimes}

        for record in trade_records:
            regime = record.get("market_regime", "Bull Trend")
            if regime not in regime_data:
                regime_data[regime] = []
            regime_data[regime].append(record.get("pnl", 0.0))

        results = []
        for reg_name, pnls in regime_data.items():
            if not pnls:
                continue

            count = len(pnls)
            wins = sum(1 for p in pnls if p > 0)
            losses = sum(abs(p) for p in pnls if p < 0)
            gross_win = sum(p for p in pnls if p > 0)

            win_rate = round((wins / count) * 100.0, 2)
            profit_factor = round(gross_win / max(losses, 1.0), 2)
            total_pnl = round(sum(pnls), 2)

            results.append(RegimePerformance(
                regime_name=reg_name,
                trade_count=count,
                win_rate=win_rate,
                profit_factor=profit_factor,
                total_pnl=total_pnl
            ))

        return results
