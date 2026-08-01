"""
RAHUUL RADAR — Phase-1 Limited Live Trading: Emergency Stop Condition Listener
==============================================================================
Monitors live trading execution for Stop Conditions: Daily Loss >1%, Weekly Loss >3%, System Failures.
"""

from typing import List, Dict, Any
from live_trading.live_models import StopConditionStatus


class EmergencyStopConditionMonitor:
    """
    Emergency Safety Circuit Breaker.
    """

    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.consecutive_failures = 0

    def evaluate_stop_conditions(
        self,
        todays_pnl: float,
        weekly_pnl: float,
        system_failures: int = 0,
        broker_anomaly: bool = False
    ) -> StopConditionStatus:
        """
        Evaluates emergency circuit breaker stop conditions.
        """
        daily_loss_pct = round((abs(min(todays_pnl, 0.0)) / self.initial_capital) * 100.0, 2)
        weekly_loss_pct = round((abs(min(weekly_pnl, 0.0)) / self.initial_capital) * 100.0, 2)

        triggers = []

        # 1. Daily Loss > 1%
        if daily_loss_pct > 1.0:
            triggers.append(f"Daily Loss ({daily_loss_pct}%) breached 1.0% limit (₹100)")

        # 2. Weekly Loss > 3%
        if weekly_loss_pct > 3.0:
            triggers.append(f"Weekly Loss ({weekly_loss_pct}%) breached 3.0% limit (₹300)")

        # 3. Two consecutive system failures
        if system_failures >= 2:
            triggers.append(f"System Failures ({system_failures}) reached threshold >= 2")

        # 4. Broker Execution Anomaly
        if broker_anomaly:
            triggers.append("Broker execution anomaly detected")

        is_stopped = len(triggers) > 0
        reason = "; ".join(triggers) if is_stopped else "NORMAL_OPERATIONS"

        return StopConditionStatus(
            is_stopped=is_stopped,
            trigger_reason=reason,
            daily_drawdown_pct=daily_loss_pct,
            weekly_drawdown_pct=weekly_loss_pct,
            system_failures_count=system_failures
        )
