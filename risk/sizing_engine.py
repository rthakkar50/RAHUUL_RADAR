from .models import RiskProfile

class SizingEngine:
    @staticmethod
    def calculate_position_size(profile: RiskProfile, entry_price: float, stop_loss: float) -> tuple[int, float]:
        """
        Calculates the quantity to buy (lot size) such that if the stop loss is hit,
        the total loss equals the maximum allowed risk per trade.
        
        Returns:
            (quantity, capital_required)
        """
        if entry_price <= stop_loss:
            return 0, 0.0
            
        risk_amount = profile.account_size * (profile.risk_per_trade_pct / 100.0)
        risk_per_share = entry_price - stop_loss
        
        if risk_per_share <= 0:
            return 0, 0.0
            
        qty = int(risk_amount // risk_per_share)
        
        capital_required = qty * entry_price
        
        return qty, capital_required

    @staticmethod
    def calculate_rr(entry_price: float, stop_loss: float, target_price: float) -> float:
        risk = entry_price - stop_loss
        reward = target_price - entry_price
        if risk <= 0:
            return 0.0
        return round(reward / risk, 2)
