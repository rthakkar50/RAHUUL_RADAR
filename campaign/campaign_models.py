"""
RAHUUL RADAR — Market Validation Campaign: Domain Models
=========================================================
Data contracts for 1,000 Trade Paper Campaign, Execution Quality, Bug Tracking, and Market Validation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class CampaignTradeRecord:
    trade_id: str
    date: str
    time: str
    symbol: str
    market_regime: str
    strategy: str  # Swing Momentum / Swing Breakout / F&O Option Buying / AI Strategy
    signal: str  # BUY / SELL
    confidence: float
    entry_price: float
    exit_price: float
    stop_loss: float
    target_1: float
    target_2: float
    risk_reward: str
    holding_mins: int
    pnl: float
    brokerage: float
    slippage: float
    reason: str


@dataclass
class ExecutionQualityMetrics:
    avg_signal_latency_ms: float
    fill_accuracy_pct: float
    avg_slippage_pts: float
    avg_order_delay_ms: float
    cancelled_orders_count: int


@dataclass
class BugReportItem:
    bug_id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    module: str
    description: str
    status: str  # OPEN, RESOLVED, MITIGATED
    timestamp: str


@dataclass
class MarketValidationSummary:
    total_trades_completed: int
    swing_trades_count: int
    fno_trades_count: int
    win_rate_pct: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown_pct: float
    avg_holding_mins: float
    avg_risk_reward: str
    ai_accuracy_pct: float
    regime_performance: Dict[str, Dict[str, Any]]
    strategy_rankings: List[Dict[str, Any]]
    execution_quality: ExecutionQualityMetrics
    bugs_count_by_severity: Dict[str, int]
    cto_go_decision: str
