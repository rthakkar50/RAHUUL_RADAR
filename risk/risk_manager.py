import logging
from .models import RiskProfile, RiskResult
from .prop_firms import get_prop_firm_validator
from .emergency import KillSwitch
from .portfolio_risk import PortfolioRiskEngine
from .sizing_engine import SizingEngine

logger = logging.getLogger("RiskManager")

class RiskManager:
    def __init__(self, profile: RiskProfile):
        self.profile = profile
        self.kill_switch = KillSwitch()
        self.portfolio_engine = PortfolioRiskEngine()
        self.prop_firm = get_prop_firm_validator(self.profile.prop_firm)
        
    def evaluate_trade(
        self,
        entry_price: float, 
        stop_loss: float,
        target_price: float,
        current_daily_drawdown: float, 
        current_total_drawdown: float,
        current_open_trades: int,
        sector: str,
        current_sector_exposure_pct: float
    ) -> RiskResult:
        """
        Evaluates a potential trade setup through all risk layers.
        """
        
        # 1. Check Kill Switch
        self.kill_switch.check_health(current_total_drawdown, self.profile.max_monthly_loss_pct)
        if self.kill_switch.is_triggered():
            return RiskResult(False, "Kill Switch Active - Trading Halted", 0, 0, 0, 0, 0, 0)
            
        # 2. Check Prop Firm Rules
        is_valid_prop, prop_reason = self.prop_firm.validate_rules(self.profile, current_daily_drawdown, current_total_drawdown)
        if not is_valid_prop:
            return RiskResult(False, prop_reason, 0, 0, 0, 0, 0, 0)
            
        # 3. Check Portfolio Exposure
        is_valid_port, port_reason = self.portfolio_engine.evaluate_exposure(self.profile, current_open_trades, sector, current_sector_exposure_pct)
        if not is_valid_port:
            return RiskResult(False, port_reason, 0, 0, 0, 0, 0, 0)
            
        # 4. Calculate Sizing
        qty, capital = SizingEngine.calculate_position_size(self.profile, entry_price, stop_loss)
        
        if qty <= 0:
            return RiskResult(False, "Invalid SL or Entry Price", 0, 0, 0, 0, 0, 0)
            
        if capital > self.profile.account_size:
            return RiskResult(False, "Insufficient Capital", 0, 0, 0, 0, 0, 0)
            
        # 5. Calculate Metrics
        max_loss = qty * (entry_price - stop_loss)
        rr = SizingEngine.calculate_rr(entry_price, stop_loss, target_price)
        
        # We enforce a minimum 1:1.5 RR for institutional trades
        if rr < 1.5:
            return RiskResult(False, f"RR {rr} is below minimum 1.5", self.profile.risk_per_trade_pct, qty, capital, max_loss, target_price, rr)
            
        return RiskResult(
            approved=True, 
            reason="Trade Approved", 
            risk_pct=self.profile.risk_per_trade_pct,
            lot_size=qty,
            capital_required=capital,
            maximum_loss=max_loss,
            recommended_target=target_price,
            recommended_rr=rr
        )
