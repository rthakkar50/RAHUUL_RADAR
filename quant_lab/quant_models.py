"""
RAHUUL RADAR — Quant Research Lab: Domain Models
=================================================
Statistical data contracts and research models for trading analytics.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional


@dataclass
class StrategyAnalytics:
    total_trades: int
    win_rate: float
    loss_rate: float
    profit_factor: float
    expectancy: float
    avg_winner: float
    avg_loser: float
    risk_reward: float
    recovery_factor: float
    ulcer_index: float


@dataclass
class EquityCurveData:
    daily_equity: List[float]
    weekly_equity: List[float]
    monthly_equity: List[float]
    drawdown_curve: List[float]
    rolling_win_rate: List[float]


@dataclass
class DrawdownMetrics:
    max_drawdown_pct: float
    current_drawdown_pct: float
    recovery_time_days: int
    longest_losing_streak: int
    largest_winner: float
    largest_loser: float


@dataclass
class MonteCarloResult:
    num_simulations: int
    prob_of_ruin_pct: float
    expected_max_drawdown_pct: float
    confidence_interval_95: Tuple[float, float]
    simulated_equity_curves: List[List[float]] = field(default_factory=list)


@dataclass
class WalkForwardResult:
    in_sample_sharpe: float
    out_of_sample_sharpe: float
    stability_ratio: float
    is_robust: bool


@dataclass
class RegimePerformance:
    regime_name: str
    trade_count: int
    win_rate: float
    profit_factor: float
    total_pnl: float


@dataclass
class RiskMetricsData:
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    information_ratio: float
    beta: float
    alpha: float
    volatility_pct: float


@dataclass
class AIPerformanceData:
    ai_accuracy_pct: float
    confidence_accuracy: float
    false_buy_pct: float
    false_sell_pct: float
    false_wait_pct: float
    prediction_drift_score: float


@dataclass
class QuantReport:
    report_type: str
    summary: StrategyAnalytics
    drawdown: DrawdownMetrics
    risk_metrics: RiskMetricsData
    ai_performance: AIPerformanceData
    regime_breakdown: List[RegimePerformance]
    generation_time_ms: float
