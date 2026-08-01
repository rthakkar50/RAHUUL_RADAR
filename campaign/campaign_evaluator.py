"""
RAHUUL RADAR — Market Validation Campaign: Evaluator (Task 3 & 4)
===================================================================
Evaluates trade performance broken down by Market Regime and Strategy type.
"""

from typing import List, Dict, Any
from campaign.campaign_models import CampaignTradeRecord


class CampaignEvaluator:
    """
    Market Regime & Strategy Evaluator Engine.
    """

    def evaluate_regimes(self, trades: List[CampaignTradeRecord]) -> Dict[str, Dict[str, Any]]:
        """Task 3: Computes performance statistics per market regime."""
        regime_map: Dict[str, List[CampaignTradeRecord]] = {}
        for t in trades:
            regime_map.setdefault(t.market_regime, []).append(t)

        results = {}
        for reg, recs in regime_map.items():
            wins = [t.pnl for t in recs if t.pnl > 0]
            losses = [abs(t.pnl) for t in recs if t.pnl < 0]
            count = len(recs)
            win_rate = round((len(wins) / count) * 100.0, 2)
            profit_factor = round(sum(wins) / max(sum(losses), 1.0), 2)
            net_pnl = round(sum(t.pnl for t in recs), 2)

            results[reg] = {
                "trade_count": count,
                "win_rate_pct": win_rate,
                "profit_factor": profit_factor,
                "net_pnl": net_pnl
            }
        return results

    def evaluate_strategies(self, trades: List[CampaignTradeRecord]) -> List[Dict[str, Any]]:
        """Task 4: Computes performance statistics per strategy type."""
        strat_map: Dict[str, List[CampaignTradeRecord]] = {}
        for t in trades:
            strat_map.setdefault(t.strategy, []).append(t)

        rankings = []
        for strat, recs in strat_map.items():
            wins = [t.pnl for t in recs if t.pnl > 0]
            losses = [abs(t.pnl) for t in recs if t.pnl < 0]
            count = len(recs)
            win_rate = round((len(wins) / count) * 100.0, 2)
            profit_factor = round(sum(wins) / max(sum(losses), 1.0), 2)
            net_pnl = round(sum(t.pnl for t in recs), 2)

            rankings.append({
                "strategy": strat,
                "trade_count": count,
                "win_rate_pct": win_rate,
                "profit_factor": profit_factor,
                "net_pnl": net_pnl
            })

        rankings.sort(key=lambda x: x["profit_factor"], reverse=True)
        for i, item in enumerate(rankings):
            item["rank"] = i + 1

        return rankings
