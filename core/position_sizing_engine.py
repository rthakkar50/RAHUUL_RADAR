import math
from core.config_manager import ConfigManager

class PositionSizingEngine:
    """
    MASTER-16: SMART POSITION SIZING ENGINE VERSION 1.0
    Calculates position size, capital allocation, and risk metrics automatically.
    Prevents emotional sizing and controls losses strictly.
    """
    
    def __init__(self):
        self.config = ConfigManager().load_config()
        
    def calculate_smart_position(self, entry, sl, volatility_atr=0.0, account_type="Margin", lot_size=1):
        """
        Calculates position size strictly based on user risk, volatility, and margin limits.
        """
        try:
            entry = float(entry)
            sl = float(sl)
            volatility_atr = float(volatility_atr)
            lot_size = int(lot_size)
        except (ValueError, TypeError):
            return self._get_empty_smart_result()
            
        if entry <= 0 or sl <= 0 or entry == sl:
            return self._get_empty_smart_result()

        capital = float(self.config.get("capital", 100000))
        risk_pct = float(self.config.get("risk_pct", 1.0))
        
        # Risk configs explicitly supported: 0.25, 0.50, 1.00, 2.00
        # "Never exceed user risk."
        max_risk_amt = capital * (risk_pct / 100.0)
        risk_per_share = abs(entry - sl)
        
        # Volatility Adjustment
        # High ATR -> Reduce Quantity. Low ATR -> Normal Quantity.
        vol_penalty_factor = 1.0
        atr_pct = (volatility_atr / entry) * 100 if entry > 0 else 0
        if atr_pct > 3.0: # Highly volatile (High ATR)
            vol_penalty_factor = 0.75 # Reduce qty by 25%
        elif atr_pct > 5.0:
            vol_penalty_factor = 0.50 # Reduce qty by 50%
            
        adjusted_max_risk = max_risk_amt * vol_penalty_factor

        # Raw Quantity Calculation
        raw_qty = int(math.floor(adjusted_max_risk / risk_per_share))
        
        # Lot Size Adjustment (F&O / Options)
        if lot_size > 1:
            # Round down to nearest lot size
            raw_qty = int(math.floor(raw_qty / lot_size) * lot_size)
            
        if raw_qty < lot_size:
            raw_qty = 0
            
        recommended_qty = raw_qty
        
        # Margin / Capital Logic based on Account Type
        capital_exposure = recommended_qty * entry
        
        if account_type.upper() == "CASH":
            margin_required = capital_exposure # 1x Leverage
        elif account_type.upper() == "MARGIN":
            margin_required = capital_exposure * 0.20 # 5x Leverage
        elif account_type.upper() in ["F&O", "PROP FIRM"]:
            margin_required = capital_exposure * 0.15 # Approx 15% margin
        elif account_type.upper() == "PAPER TRADING":
            margin_required = 0.0 # No real margin limits
        else:
            margin_required = capital_exposure
            
        # Margin Check (Loss Control)
        # "Never allow Oversized Position, Revenge Sizing, Double Quantity, Random Quantity"
        if margin_required > capital and recommended_qty > 0:
            # Attempt to reduce size to fit margin
            if lot_size == 1:
                affordable_qty = int(math.floor(capital / (entry * (margin_required/capital_exposure))))
                recommended_qty = min(recommended_qty, affordable_qty)
            else:
                affordable_lots = int(math.floor(capital / (entry * lot_size * (margin_required/capital_exposure))))
                recommended_qty = affordable_lots * lot_size
                
            # Recalculate margin
            capital_exposure = recommended_qty * entry
            margin_required = capital_exposure * (margin_required/max(1, capital_exposure)) if capital_exposure > 0 else 0
            
        actual_risk = recommended_qty * risk_per_share
        remaining_capital = capital - margin_required
        
        # Final Decision Logic
        if recommended_qty == 0:
            decision = "REJECT"
        elif vol_penalty_factor < 1.0 or actual_risk < (raw_qty * risk_per_share):
            decision = "REDUCE SIZE"
        else:
            decision = "ALLOW"
            
        return {
            "Recommended Quantity": recommended_qty,
            "Capital Used": capital_exposure,
            "Risk Amount": actual_risk,
            "Margin Used": margin_required,
            "Remaining Capital": remaining_capital,
            "Final Decision": decision,
            "Account Type": account_type
        }
        
    def _get_empty_smart_result(self):
        return {
            "Recommended Quantity": 0,
            "Capital Used": 0.0,
            "Risk Amount": 0.0,
            "Margin Used": 0.0,
            "Remaining Capital": 0.0,
            "Final Decision": "REJECT",
            "Account Type": "UNKNOWN"
        }

    # =========================================================================
    # BACKWARD COMPATIBILITY LAYER
    # Maintains compatibility with the rest of the application UI/Engines
    # =========================================================================
    
    def calculate_size(self, entry, sl, mode="SWING"):
        """
        Calculates position size using the old schema, routing through the Smart Engine.
        """
        # Map old 'mode' to 'account_type'
        acct_type = "Cash"
        lot_size = 1
        
        if mode in ["INTRADAY", "SCALPING"]:
            acct_type = "Margin"
        elif mode == "F&O":
            acct_type = "F&O"
            # Simulate lot size backwards compatibility
            try:
                lot_size = max(1, int(800000 / float(entry)))
            except:
                lot_size = 500
                
        smart_res = self.calculate_smart_position(entry, sl, volatility_atr=0.0, account_type=acct_type, lot_size=lot_size)
        
        capital = float(self.config.get("capital", 100000))
        max_risk_amt = capital * (float(self.config.get("risk_pct", 1.0)) / 100.0)
        
        return {
            "risk_amount": smart_res["Risk Amount"],
            "recommended_qty": smart_res["Recommended Quantity"],
            "capital_required": smart_res["Capital Used"],
            "margin_required": smart_res["Margin Used"],
            "risk_per_share": abs(float(entry) - float(sl)) if entry and sl else 0,
            "classification": self._classify_risk(smart_res["Risk Amount"], max_risk_amt, capital),
            "max_allowed_risk": max_risk_amt,
            "is_fno": mode == "F&O"
        }
        
    def calculate_options_risk(self, premium_entry, stop_loss_premium, lot_size=25):
        """
        Calculates risk for Options Mode.
        """
        smart_res = self.calculate_smart_position(premium_entry, stop_loss_premium, volatility_atr=0.0, account_type="F&O", lot_size=lot_size)
        
        capital = float(self.config.get("capital", 100000))
        max_risk_amt = capital * (float(self.config.get("risk_pct", 1.0)) / 100.0)
        
        recommended_lots = int(smart_res["Recommended Quantity"] / max(1, lot_size))
        
        return {
            "risk_amount": smart_res["Risk Amount"],
            "recommended_lots": recommended_lots,
            "total_qty": smart_res["Recommended Quantity"],
            "capital_required": smart_res["Capital Used"],
            "premium_cost": float(premium_entry) * lot_size if premium_entry else 0,
            "classification": self._classify_risk(smart_res["Risk Amount"], max_risk_amt, capital),
            "max_allowed_risk": max_risk_amt,
            "is_options": True
        }

    def _classify_risk(self, actual_risk, max_risk_amt, capital):
        if actual_risk == 0:
            return "N/A"
            
        pct_of_max = (actual_risk / max_risk_amt) * 100 if max_risk_amt > 0 else 100
        
        if pct_of_max <= 50:
            return "Low Risk"
        elif pct_of_max <= 80:
            return "Medium Risk"
        elif pct_of_max <= 100:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def _get_empty_result(self):
        return {
            "risk_amount": 0.0,
            "recommended_qty": 0,
            "capital_required": 0.0,
            "margin_required": 0.0,
            "risk_per_share": 0.0,
            "classification": "N/A",
            "max_allowed_risk": 0.0
        }
