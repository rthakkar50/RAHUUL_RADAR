"""
RAHUUL RADAR — F&O Engine: Risk Engine (Task 11)
================================================
Dedicated Derivatives Risk Management Engine.
Calculates Lot Size, Capital Allocation, Margin Requirements,
Stop Loss, Targets, Risk-to-Reward Ratio, and Maximum Daily Loss limit.
"""

from typing import Dict, Any
from core.fno_engine.fno_models import FNORiskReport
from core.fno_engine.symbol_manager import FNOSymbolManager


class FNORiskEngine:
    """
    F&O Capital Allocation & Risk Management Engine.
    """

    def __init__(self, total_capital: float = 500000.0, max_daily_loss_pct: float = 2.0):
        self.total_capital = total_capital
        self.max_daily_loss_limit = (total_capital * max_daily_loss_pct) / 100.0
        self.symbol_manager = FNOSymbolManager()

    def calculate_risk_parameters(
        self,
        symbol: str,
        entry_price: float,
        spot_price: float,
        action: str = "BUY",
        risk_per_trade_pct: float = 1.0,
        custom_lot_count: int = 1
    ) -> FNORiskReport:
        """
        Calculates position size, stop loss, targets, margin, and risk bounds.
        """
        lot_size = self.symbol_manager.get_lot_size(symbol)
        
        # Max risk amount per trade
        max_risk_amount = (self.total_capital * (risk_per_trade_pct / 100.0))
        
        num_lots = max(custom_lot_count, 1)
        total_quantity = lot_size * num_lots

        # Capital / Premium Allocation
        capital_allocation = round(entry_price * total_quantity, 2)
        margin_required = capital_allocation  # For options buying (100% premium)

        # Stop Loss: 20% of premium for option buying, or 1% of spot
        sl_points = max(entry_price * 0.20, 5.0)
        stop_loss = round(max(entry_price - sl_points if action == "BUY" else entry_price + sl_points, 0.5), 2)

        # Targets: T1 (1:1.5 RR), T2 (1:2.5 RR), T3 (1:4 RR)
        target_1 = round(entry_price + (sl_points * 1.5) if action == "BUY" else max(entry_price - (sl_points * 1.5), 0.5), 2)
        target_2 = round(entry_price + (sl_points * 2.5) if action == "BUY" else max(entry_price - (sl_points * 2.5), 0.5), 2)
        target_3 = round(entry_price + (sl_points * 4.0) if action == "BUY" else max(entry_price - (sl_points * 4.0), 0.5), 2)

        max_risk = round(sl_points * total_quantity, 2)
        risk_reward = round(1.5, 2)

        return FNORiskReport(
            lot_size=lot_size,
            num_lots=num_lots,
            capital_allocation=capital_allocation,
            margin_required=margin_required,
            max_risk=max_risk,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            target_3=target_3,
            risk_reward=risk_reward,
            max_daily_loss=self.max_daily_loss_limit
        )
