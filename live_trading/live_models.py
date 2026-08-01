"""
RAHUUL RADAR — Phase-1 Limited Live Trading: Domain Models
============================================================
Data contracts for Live Trading Phase-1 Execution, Risk Limits, Emergency Stop Gates, and Live Audit Records.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class LiveTradeRecord:
    trade_id: str
    date: str
    time: str
    broker_order_id: str
    ai_signal: str
    confidence: float
    entry_price: float
    exit_price: float
    actual_fill_price: float
    slippage: float
    broker_charges: float
    taxes: float
    latency_ms: float
    pnl: float
    net_pnl: float
    risk_pct: float
    reason: str
    market_regime: str


@dataclass
class CapitalPhaseLimits:
    phase_name: str  # Phase-1 (₹10,000) / Phase-2 (₹25,000) / Phase-3 (₹50,000)
    capital_balance: float
    max_risk_per_trade_pct: float
    max_daily_loss_pct: float
    max_weekly_loss_pct: float
    manual_confirmation_required: bool = True


@dataclass
class StopConditionStatus:
    is_stopped: bool
    trigger_reason: str
    daily_drawdown_pct: float
    weekly_drawdown_pct: float
    system_failures_count: int


@dataclass
class LiveValidationSummary:
    total_live_trades_completed: int
    phase_1_capital: float
    gross_pnl: float
    total_charges_and_taxes: float
    net_pnl_after_charges: float
    win_rate_pct: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown_pct: float
    avg_slippage_pts: float
    avg_latency_ms: float
    risk_violations_count: int
    critical_bugs_count: int
    audit_trail_completeness_pct: float
    final_recommendation: str  # GO TO PHASE-2 / ROLL BACK TO PAPER TRADING
