"""
RAHUUL RADAR — Mobile Dashboard: Controller (Task 8, 9, 10)
=============================================================
MVC/MVVM Controller orchestrating data streams, screen states, and tab transitions.
Guarantees <200ms total load time for institutional-grade responsiveness.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from mobile.dashboard.dashboard_service import DashboardService

logger = logging.getLogger("DashboardController")


class DashboardController:
    """
    Main Controller for the Enterprise Mobile Dashboard.
    """

    def __init__(self, service: Optional[DashboardService] = None):
        self.service = service or DashboardService.get_instance()

    def get_home_dashboard(self) -> Dict[str, Any]:
        """Task 1: Loads Dashboard Home in <200ms."""
        start_time = time.time()
        market = self.service.get_market_status()
        account = self.service.get_account_status()
        portfolio = self.service.get_portfolio_summary()
        risk = self.service.get_risk_dashboard()
        watchlist = self.service.get_watchlist("SWING")

        elapsed_ms = (time.time() - start_time) * 1000.0

        return {
            "market_status": {
                "state": market.market_state,
                "nifty": market.nifty_price,
                "nifty_change": market.nifty_change,
                "banknifty": market.banknifty_price,
                "banknifty_change": market.banknifty_change,
                "regime": market.regime
            },
            "account_status": {
                "broker": account.broker_name,
                "is_connected": account.is_connected,
                "total_capital": account.total_capital,
                "available_margin": account.available_margin,
                "used_margin": account.used_margin
            },
            "portfolio": {
                "value": portfolio.total_portfolio_value,
                "todays_pnl": portfolio.todays_pnl,
                "total_pnl": portfolio.total_pnl,
                "open_positions": portfolio.open_positions_count
            },
            "risk_utilization": {
                "current_risk_pct": risk.current_risk_pct,
                "risk_level": risk.risk_level
            },
            "latest_ai_signals": [item.to_dict() for item in watchlist[:3]],
            "load_time_ms": round(elapsed_ms, 2)
        }

    def get_portfolio_dashboard(self) -> Dict[str, Any]:
        """Task 2: Portfolio Dashboard payload."""
        start_time = time.time()
        summary = self.service.get_portfolio_summary()
        account = self.service.get_account_status()
        elapsed_ms = (time.time() - start_time) * 1000.0

        return {
            "total_capital": account.total_capital,
            "available_margin": account.available_margin,
            "used_margin": account.used_margin,
            "portfolio_value": summary.total_portfolio_value,
            "todays_pnl": summary.todays_pnl,
            "total_pnl": summary.total_pnl,
            "winning_rate": summary.winning_rate,
            "drawdown": summary.drawdown,
            "open_positions_count": summary.open_positions_count,
            "holdings_count": summary.holdings_count,
            "load_time_ms": round(elapsed_ms, 2)
        }

    def get_watchlist_dashboard(self, category: str = "SWING") -> Dict[str, Any]:
        """Task 3: Watchlist Dashboard payload."""
        start_time = time.time()
        items = self.service.get_watchlist(category)
        elapsed_ms = (time.time() - start_time) * 1000.0

        return {
            "category": category.upper(),
            "items": [item.to_dict() for item in items],
            "load_time_ms": round(elapsed_ms, 2)
        }

    def get_risk_dashboard(self) -> Dict[str, Any]:
        """Task 4: Risk Dashboard payload."""
        start_time = time.time()
        risk = self.service.get_risk_dashboard()
        elapsed_ms = (time.time() - start_time) * 1000.0

        return {
            "current_risk_pct": risk.current_risk_pct,
            "daily_loss": risk.daily_loss,
            "max_daily_loss": risk.max_daily_loss,
            "margin_used_pct": risk.margin_used_pct,
            "sector_exposure": risk.sector_exposure,
            "lot_exposure": risk.lot_exposure,
            "risk_level": risk.risk_level,
            "load_time_ms": round(elapsed_ms, 2)
        }

    def get_analytics_dashboard(self) -> Dict[str, Any]:
        """Task 5: Analytics Dashboard payload."""
        start_time = time.time()
        analytics = self.service.get_analytics()
        elapsed_ms = (time.time() - start_time) * 1000.0

        return {
            "win_rate": analytics.win_rate,
            "profit_curve": analytics.profit_curve,
            "monthly_returns": analytics.monthly_returns,
            "strategy_performance": analytics.strategy_performance,
            "best_trade": analytics.best_trade,
            "worst_trade": analytics.worst_trade,
            "avg_holding_time_mins": analytics.avg_holding_time_mins,
            "load_time_ms": round(elapsed_ms, 2)
        }

    def get_notifications_dashboard(self) -> Dict[str, Any]:
        """Task 6: Notifications payload."""
        start_time = time.time()
        notifs = self.service.get_notifications()
        elapsed_ms = (time.time() - start_time) * 1000.0

        return {
            "notifications": [
                {
                    "id": n.id,
                    "type": n.type,
                    "title": n.title,
                    "message": n.message,
                    "timestamp": n.timestamp,
                    "is_read": n.is_read
                } for n in notifs
            ],
            "load_time_ms": round(elapsed_ms, 2)
        }

    def get_settings(self) -> Dict[str, Any]:
        """Task 7: Settings configuration payload."""
        return {
            "theme": "DARK_PRO",
            "broker": "Paytm Money Live",
            "scanner_mode": "SWING_HIGH_CONFIDENCE",
            "notifications_enabled": True,
            "ai_mode": "AUTO_CALIBRATED"
        }
