import os
import json
import logging
from datetime import datetime
from core.config_manager import ConfigManager
from core.position_sizing_engine import PositionSizingEngine

class RiskManager:
    """
    Singleton Risk Management Engine (SPRINT-75).
    Tracks daily risk limits, max open positions, and prevents overallocation.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self.config = ConfigManager().load_config()
        self.position_engine = PositionSizingEngine()
        
        # Setup specific logger
        self.log_path = os.path.join(os.getcwd(), "logs", "risk_manager.log")
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self.logger = logging.getLogger("risk_manager")
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            fh = logging.FileHandler(self.log_path)
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(fh)
            
        self.logger.info("Risk Management Engine Initialized.")
        
    def evaluate_trade_risk(self, symbol, entry, sl, mode="SWING"):
        """
        Calculates position size and validates against max risk rules.
        Returns (is_valid, size_data, rejections).
        """
        size_data = self.position_engine.calculate_size(entry, sl, mode)
        
        # Validate rules
        rejections = []
        actual_risk = size_data.get("risk_amount", 0)
        max_risk_allowed = size_data.get("max_allowed_risk", 0)
        
        # 1. Over max risk per trade
        if actual_risk > max_risk_allowed:
            rejections.append(f"Risk Amount (₹{actual_risk:,.0f}) exceeds allowed limit (₹{max_risk_allowed:,.0f})")
            
        # 2. Insufficient Capital (for the recommended qty)
        capital = float(self.config.get("capital", 100000))
        cap_req = size_data.get("capital_required", 0)
        margin_req = size_data.get("margin_required", cap_req)
        
        if margin_req > capital:
            rejections.append(f"Insufficient Capital: Required ₹{margin_req:,.0f}, Available: ₹{capital:,.0f}")
            
        # 3. Check Daily Loss Limit (This would normally hook into paper trading/live PnL)
        # Assuming we just check if it's set in config for now
        max_daily_loss = float(self.config.get("max_daily_loss", 0))
        if max_daily_loss > 0:
            # Need to get today's realized PnL. (Mocking for now, as this is a decision engine)
            # In a full system, we query PaperTradingEngine
            try:
                from application.paper_trading_service import PaperTradingEngine
                pt = PaperTradingEngine.get_instance()
                today_pnl = sum(p.get('net_pnl', 0) for p in pt.closed_positions.values() if p['exit_time'].startswith(datetime.now().strftime("%Y-%m-%d")))
                if today_pnl < -max_daily_loss:
                    rejections.append(f"Daily Loss Limit Exceeded (₹{today_pnl:,.0f} < -₹{max_daily_loss:,.0f})")
            except Exception as e:
                self.logger.error(f"Error checking daily PnL: {e}")
                
        # 4. Max Open Positions
        max_open = int(self.config.get("max_open_positions", 0))
        if max_open > 0:
            try:
                from application.paper_trading_service import PaperTradingEngine
                pt = PaperTradingEngine.get_instance()
                open_count = len(pt.active_positions)
                if open_count >= max_open:
                    rejections.append(f"Max Open Positions Limit Reached ({open_count})")
            except Exception:
                pass
                
        # 5. Risk / Reward check (if available in size_data, usually passed from SetupEngine, 
        # but MasterAI handles RR rejections separately).

        is_valid = len(rejections) == 0
        
        if not is_valid:
            self.logger.warning(f"Trade Rejected by Risk Manager - Symbol: {symbol}, Rejections: {rejections}")
        else:
            self.logger.info(f"Trade Approved - Symbol: {symbol}, Risk: ₹{actual_risk:,.0f}, Qty: {size_data.get('recommended_qty')}")
            
        return is_valid, size_data, rejections

    def get_live_risk_summary(self):
        """
        Returns data for the Live Risk Panel in Portfolio.
        """
        capital = float(self.config.get("capital", 100000))
        risk_pct = float(self.config.get("risk_pct", 1.0))
        max_daily_loss = float(self.config.get("max_daily_loss", 5000))
        max_open_positions = int(self.config.get("max_open_positions", 5))
        
        # Calculate current usage
        open_risk = 0.0
        open_exposure = 0.0
        today_pnl = 0.0
        open_pos_count = 0
        
        try:
            from application.paper_trading_service import PaperTradingEngine
            pt = PaperTradingEngine.get_instance()
            
            # Active positions risk
            for p in pt.active_positions.values():
                qty = float(p.get("qty", 0))
                entry = float(p.get("entry_price", 0))
                sl = float(p.get("sl", 0))
                if sl > 0:
                    open_risk += (abs(entry - sl) * qty)
                open_exposure += (entry * qty)
                
            open_pos_count = len(pt.active_positions)
            
            # Today's Realized PnL
            today_date = datetime.now().strftime("%Y-%m-%d")
            today_pnl = sum(p.get('net_pnl', 0) for p in pt.closed_positions.values() if p['exit_time'].startswith(today_date))
            
        except Exception:
            pass
            
        remaining_risk = max_daily_loss - abs(min(0, today_pnl))
        if remaining_risk < 0: remaining_risk = 0
        
        return {
            "capital": capital,
            "max_daily_loss": max_daily_loss,
            "today_pnl": today_pnl,
            "open_risk": open_risk,
            "open_exposure": open_exposure,
            "remaining_risk": remaining_risk,
            "max_open_positions": max_open_positions,
            "current_open_positions": open_pos_count
        }
