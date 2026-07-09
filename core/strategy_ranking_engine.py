import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class RankingStatus(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    AVERAGE = "AVERAGE"
    POOR = "POOR"
    REJECTED = "REJECTED"

@dataclass
class StrategyMetrics:
    strategy_name: str
    win_rate: float
    profit_factor: float
    expectancy: float
    average_rr: float
    maximum_drawdown: float
    net_profit: float
    total_trades: int
    average_holding_time: float
    validation_status: str

    def to_dict(self) -> dict:
        return {
            "strategy_name": self.strategy_name,
            "win_rate": self.win_rate,
            "profit_factor": self.profit_factor,
            "expectancy": self.expectancy,
            "average_rr": self.average_rr,
            "maximum_drawdown": self.maximum_drawdown,
            "net_profit": self.net_profit,
            "total_trades": self.total_trades,
            "average_holding_time": self.average_holding_time,
            "validation_status": self.validation_status
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'StrategyMetrics':
        return cls(
            strategy_name=data.get("strategy_name", "UNKNOWN"),
            win_rate=float(data.get("win_rate", 0.0)),
            profit_factor=float(data.get("profit_factor", 0.0)),
            expectancy=float(data.get("expectancy", 0.0)),
            average_rr=float(data.get("average_rr", 0.0)),
            maximum_drawdown=float(data.get("maximum_drawdown", 0.0)),
            net_profit=float(data.get("net_profit", 0.0)),
            total_trades=int(data.get("total_trades", 0)),
            average_holding_time=float(data.get("average_holding_time", 0.0)),
            validation_status=data.get("validation_status", "UNKNOWN")
        )

@dataclass
class StrategyRank:
    rank: int
    strategy_name: str
    overall_score: float
    confidence: str
    remarks: str

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "strategy_name": self.strategy_name,
            "overall_score": self.overall_score,
            "confidence": self.confidence,
            "remarks": self.remarks
        }


class StrategyRankingEngine:
    def __init__(self, config_path: str = "config/strategy_ranking.json"):
        self.config_path = config_path
        self.weights = {}
        self.thresholds = {}
        self.status_thresholds = {}
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.weights = data.get("ranking_weights", {})
                self.thresholds = data.get("ranking_thresholds", {})
                self.status_thresholds = data.get("status_thresholds", {})
        except Exception as e:
            logger.error(f"Failed to load config {self.config_path}: {e}")
            self.weights = {
                "win_rate_weight": 0.25,
                "profit_factor_weight": 0.25,
                "drawdown_weight": 0.15,
                "expectancy_weight": 0.15,
                "risk_reward_weight": 0.10,
                "trade_count_weight": 0.10
            }
            self.thresholds = {
                "minimum_validation_score": 40.0
            }
            self.status_thresholds = {
                "excellent_score": 85.0,
                "good_score": 70.0,
                "average_score": 55.0,
                "poor_score": 40.0
            }

    def validate_metrics(self, metrics: StrategyMetrics) -> bool:
        """Validates that metrics are mathematically possible and not malformed."""
        if metrics.total_trades < 0:
            return False
        if metrics.win_rate < 0.0 or metrics.win_rate > 100.0:
            return False
        if metrics.profit_factor < 0.0:
            return False
        if metrics.maximum_drawdown < 0.0 or metrics.maximum_drawdown > 100.0:
            return False
        return True

    def _normalize_score(self, value: float, min_val: float, max_val: float) -> float:
        """Helper to normalize a value between 0 and 100 based on expected bounds."""
        if max_val == min_val:
            return 0.0
        normalized = ((value - min_val) / (max_val - min_val)) * 100.0
        # Clamp between 0 and 100
        return max(0.0, min(100.0, normalized))

    def calculate_overall_score(self, metrics: StrategyMetrics) -> float:
        """Calculates a weighted score from 0 to 100 based on configuration weights."""
        if not self.validate_metrics(metrics):
            return 0.0

        # Normalizations
        # Win Rate: 0 to 100 is naturally 0 to 100
        wr_score = metrics.win_rate
        
        # Profit Factor: 0 to 5.0 (cap at 5.0 for scoring purposes)
        pf_score = self._normalize_score(metrics.profit_factor, 0.0, 5.0)
        
        # Drawdown: Inverted! Lower drawdown is better. 100% drawdown = 0 score. 0% = 100 score.
        dd_score = 100.0 - metrics.maximum_drawdown
        
        # Expectancy: Assume 0 to 1.0 expectancy for scoring bounds
        exp_score = self._normalize_score(metrics.expectancy, 0.0, 1.0)
        
        # Average RR: Assume 0 to 5.0 for scoring bounds
        rr_score = self._normalize_score(metrics.average_rr, 0.0, 5.0)
        
        # Trade Count: Assume 0 to 1000 for scoring bounds
        tc_score = self._normalize_score(metrics.total_trades, 0, 1000)

        weights = self.weights
        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.0
            
        score = (
            (wr_score * weights.get("win_rate_weight", 0.0)) +
            (pf_score * weights.get("profit_factor_weight", 0.0)) +
            (dd_score * weights.get("drawdown_weight", 0.0)) +
            (exp_score * weights.get("expectancy_weight", 0.0)) +
            (rr_score * weights.get("risk_reward_weight", 0.0)) +
            (tc_score * weights.get("trade_count_weight", 0.0))
        ) / total_weight

        return max(0.0, min(100.0, score))

    def _determine_status(self, score: float, metrics: StrategyMetrics) -> RankingStatus:
        if not self.validate_metrics(metrics):
            return RankingStatus.REJECTED
            
        if metrics.validation_status.upper() == "FAILED":
            return RankingStatus.REJECTED

        if score < self.thresholds.get("minimum_validation_score", 40.0):
            return RankingStatus.REJECTED

        if score >= self.status_thresholds.get("excellent_score", 85.0):
            return RankingStatus.EXCELLENT
        elif score >= self.status_thresholds.get("good_score", 70.0):
            return RankingStatus.GOOD
        elif score >= self.status_thresholds.get("average_score", 55.0):
            return RankingStatus.AVERAGE
        else:
            return RankingStatus.POOR

    def rank_strategies(self, strategies: List[StrategyMetrics]) -> List[StrategyRank]:
        """Ranks a list of strategies and returns them sorted by overall score."""
        start_time = __import__("datetime").datetime.now()
        logger.info("Ranking Start")

        scored_strategies = []
        for metrics in strategies:
            score = self.calculate_overall_score(metrics)
            status = self._determine_status(score, metrics)
            
            if status == RankingStatus.REJECTED:
                remarks = "Rejected due to invalid metrics, failed validation, or score below minimum."
            else:
                remarks = f"Metrics validated. Win Rate: {metrics.win_rate:.1f}%, PF: {metrics.profit_factor:.2f}"
                
            scored_strategies.append({
                "metrics": metrics,
                "score": score,
                "status": status,
                "remarks": remarks
            })

        # Sort descending by score, tie-break by net_profit
        scored_strategies.sort(key=lambda x: (x["score"], x["metrics"].net_profit), reverse=True)

        ranked_results = []
        rank_counter = 1
        for item in scored_strategies:
            ranked_results.append(StrategyRank(
                rank=rank_counter,
                strategy_name=item["metrics"].strategy_name,
                overall_score=round(item["score"], 2),
                confidence=item["status"].value,
                remarks=item["remarks"]
            ))
            rank_counter += 1

        elapsed = (__import__("datetime").datetime.now() - start_time).total_seconds()
        logger.info(f"Ranking Complete in {elapsed:.3f}s")
        return ranked_results

    def get_best_strategy(self, ranks: List[StrategyRank]) -> Optional[StrategyRank]:
        """Returns the best strategy that is not rejected."""
        valid_ranks = [r for r in ranks if r.confidence != RankingStatus.REJECTED.value]
        if not valid_ranks:
            return None
        return valid_ranks[0]

    def get_top_n(self, ranks: List[StrategyRank], n: int) -> List[StrategyRank]:
        """Returns the top N strategies that are not rejected."""
        valid_ranks = [r for r in ranks if r.confidence != RankingStatus.REJECTED.value]
        return valid_ranks[:n]

    def generate_ranking_report(self, ranks: List[StrategyRank]) -> dict:
        """Generates a structured overview of the strategy rankings."""
        if not ranks:
            return {"status": "EMPTY", "message": "No strategies provided for ranking."}

        valid_ranks = [r for r in ranks if r.confidence != RankingStatus.REJECTED.value]
        rejected_ranks = [r for r in ranks if r.confidence == RankingStatus.REJECTED.value]
        
        top_strategy = valid_ranks[0].strategy_name if valid_ranks else "None"
        worst_strategy = valid_ranks[-1].strategy_name if valid_ranks else "None"

        return {
            "Overall Ranking": [r.to_dict() for r in ranks],
            "Top Strategy": top_strategy,
            "Worst Strategy": worst_strategy,
            "Summary": {
                "Total Evaluated": len(ranks),
                "Total Accepted": len(valid_ranks),
                "Total Rejected": len(rejected_ranks)
            },
            "Recommendations": f"Consider allocating primary capital to {top_strategy}. Review rejected strategies for logic errors." if valid_ranks else "No valid strategies found."
        }
