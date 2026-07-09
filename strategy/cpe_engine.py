from typing import Dict, List
import time
from datetime import datetime, timedelta

class CapitalProtectionEngine:
    """
    CAPITAL PROTECTION ENGINE (CPE) V2.0
    The Master Firewall. Highest priority engine in the AI.
    Mission: PROTECT TRADING CAPITAL.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CapitalProtectionEngine()
        return cls._instance

    def __init__(self):
        # Default limits
        self.max_daily_loss_pct = 2.0
        self.max_open_trades = 3
        self.max_consecutive_losses = 3
        self.max_capital_exposure_pct = 30.0
        self.max_position_risk_pct = 1.0
        
        # State tracking (would normally be persisted to DB)
        self.daily_pnl_pct = 0.0
        self.consecutive_losses = 0
        self.open_trades_count = 0
        self.current_exposure_pct = 0.0
        self.total_trades_today = 0
        
        # Cooldown State
        self.cooldown_active = False
        self.cooldown_until = None
        self.cooldown_duration_mins = 15
        
        # Last trade memory for Revenge Trading check
        self.last_exited_symbol = None
        self.last_exit_time = None
        self.last_exit_pnl = 0

    def register_trade_exit(self, symbol: str, pnl_pct: float):
        """Update state when a trade closes."""
        self.open_trades_count = max(0, self.open_trades_count - 1)
        self.daily_pnl_pct += pnl_pct
        self.last_exited_symbol = symbol
        self.last_exit_time = datetime.now()
        self.last_exit_pnl = pnl_pct
        
        if pnl_pct < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
            
        # Trigger cooldown if consecutive losses reached
        if self.consecutive_losses >= self.max_consecutive_losses:
            self._activate_cooldown("Loss Streak Limit Reached")

    def register_trade_entry(self, position_size_pct: float):
        """Update state when a trade opens."""
        self.open_trades_count += 1
        self.total_trades_today += 1
        self.current_exposure_pct += position_size_pct
        
    def _activate_cooldown(self, reason: str):
        self.cooldown_active = True
        self.cooldown_until = datetime.now() + timedelta(minutes=self.cooldown_duration_mins)
        
    def check_cooldown(self):
        if self.cooldown_active:
            if datetime.now() >= self.cooldown_until:
                self.cooldown_active = False
                self.cooldown_until = None
            return self.cooldown_active
        return False

    def validate_entry(self, symbol: str, risk_pct: float, exposure_pct: float, market_quality: str) -> Dict:
        """
        Validates if a new trade should be allowed.
        Returns: {"cpe_status": str, "cpe_score": int, "cpe_reason": str}
        """
        score = 100
        reasons = []
        
        # 1. Daily Loss Limit
        if self.daily_pnl_pct <= -self.max_daily_loss_pct:
            return {"cpe_status": "STOP TRADING TODAY", "cpe_score": 0, "cpe_reason": "Daily Loss Limit Reached"}
            
        # 2 & 12. Cooldown & Consecutive Losses
        if self.check_cooldown():
            time_left = int((self.cooldown_until - datetime.now()).total_seconds() / 60)
            return {"cpe_status": "BLOCK TRADE", "cpe_score": 0, "cpe_reason": f"Cooling Mode Active ({time_left}m left)"}
            
        # 3. Maximum Open Trades
        if self.open_trades_count >= self.max_open_trades:
            return {"cpe_status": "BLOCK TRADE", "cpe_score": 0, "cpe_reason": "Max Open Trades Reached"}
            
        # 4. Total Capital Exposure
        if (self.current_exposure_pct + exposure_pct) > self.max_capital_exposure_pct:
            return {"cpe_status": "BLOCK TRADE", "cpe_score": 0, "cpe_reason": "Max Capital Exposure Exceeded"}
            
        # 5. Position Risk
        if risk_pct > self.max_position_risk_pct:
            return {"cpe_status": "BLOCK TRADE", "cpe_score": 0, "cpe_reason": "Max Risk Per Trade Exceeded"}
            
        # 7. Market Quality
        if market_quality == "POOR":
            score -= 20
            reasons.append("Poor Market Breadth")
            
        # 9. Overtrading Detection
        if self.total_trades_today > 10:
            score -= 15
            reasons.append("Overtrading Risk")
            
        # 10. Revenge Trading Detection
        if self.last_exited_symbol == symbol and self.last_exit_pnl < 0:
            if self.last_exit_time and (datetime.now() - self.last_exit_time).total_seconds() < 900: # 15 mins
                score -= 30
                reasons.append("Revenge Trading Risk")
                
        # 13. Capital Safety Score
        if self.consecutive_losses > 0:
            score -= (self.consecutive_losses * 10)
            
        score = max(0, min(100, score))
        
        if score >= 90:
            status = "ALLOW TRADE"
        elif score >= 70:
            status = "WAIT"
        else:
            status = "BLOCK TRADE"
            
        final_reason = " | ".join(reasons) if reasons else "Trade Safe"
            
        return {
            "cpe_status": status,
            "cpe_score": score,
            "cpe_reason": final_reason
        }

    def get_dashboard_stats(self) -> Dict:
        return {
            "daily_pnl_pct": self.daily_pnl_pct,
            "daily_risk_limit": self.max_daily_loss_pct,
            "open_trades": self.open_trades_count,
            "exposure": self.current_exposure_pct,
            "loss_streak": self.consecutive_losses,
            "cooldown_active": self.check_cooldown(),
            "safety_score": 100 - (self.consecutive_losses * 10) if not self.check_cooldown() else 0
        }
