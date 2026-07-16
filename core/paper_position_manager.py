import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from core.models.paper_portfolio_models import PaperPosition

logger = logging.getLogger("PaperPositionManager")

class PaperPositionManager:
    """
    Evaluates paper positions against multi-level targets, trailing stops, and time exits.
    Does not modify portfolio capital directly; triggers callbacks/returns actions.
    """
    def __init__(self, portfolio_engine):
        self.portfolio = portfolio_engine
        
    def evaluate_positions(self, prices_dict: Dict[str, float]) -> List[Tuple[str, float, str, Optional[int]]]:
        """
        Evaluate all open positions for exit conditions based on the new prices.
        Returns a list of exit commands: [(position_id, exit_price, reason, close_qty), ...]
        """
        exits_to_process = []
        
        for pid, pos in self.portfolio.open_positions.items():
            if pos.symbol in prices_dict:
                cmp = prices_dict[pos.symbol]
                
                # The trailing stop update check (using percentage trailing)
                self._update_trailing_stop(pos, cmp)
                
                exit_reason, close_qty = self._check_exit_conditions(pos, cmp)
                if exit_reason:
                    exits_to_process.append((pid, cmp, exit_reason, close_qty))
                    
        return exits_to_process

    def _update_trailing_stop(self, pos: PaperPosition, cmp: float):
        """
        Percentage-based Trailing Stop logic.
        If trailing_stop > 0, we treat it as a percentage distance (e.g., 2.0 for 2%).
        """
        if pos.trailing_stop <= 0:
            return
            
        trail_pct = pos.trailing_stop / 100.0
        
        if pos.direction == 'BUY':
            trail_level = cmp * (1 - trail_pct)
            # Only trail up, never down. Ensure effective_sl is initialized.
            if pos.sl == 0 or trail_level > pos.sl:
                pos.sl = trail_level
        else: # SELL
            trail_level = cmp * (1 + trail_pct)
            # Only trail down, never up.
            if pos.sl == 0 or trail_level < pos.sl:
                pos.sl = trail_level

    def _check_exit_conditions(self, pos: PaperPosition, cmp: float) -> Tuple[Optional[str], Optional[int]]:
        """
        Checks fixed SL, multi-targets, and time exits.
        Returns (reason, close_qty) if an exit is triggered, else (None, None).
        For T1 and T2, we perform partial exits (e.g., 33% of original position).
        """
        # Time Exit Check
        if pos.time_exit_dt:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if now_str >= pos.time_exit_dt:
                return "Time Exit", pos.qty
                
        # Trailing Stop Check (since pos.sl is updated by _update_trailing_stop)
        effective_sl = pos.sl

        if pos.direction == 'BUY':
            if cmp <= effective_sl and effective_sl > 0:
                return "SL/Trail Hit", pos.qty
                
            # Highest target reached (Full close)
            if pos.target_3 > 0 and cmp >= pos.target_3:
                return "Target 3 Hit", pos.qty
                
            # Target 2 (Partial close if not already triggered)
            # Since we modify qty, we could just close a fixed chunk, say max(1, pos.qty // 2)
            # For simplicity, if we hit T2 and we still have substantial qty, close 50%
            if pos.target_2 > 0 and cmp >= pos.target_2:
                # To prevent endless loop of T2 hits on same price, we could check if T2 was already hit,
                # but removing target_2 once hit is the safest way.
                pos.target_2 = 0.0 # Clear target once hit
                return "Target 2 Hit", max(1, pos.qty // 2)
                
            if pos.target_1 > 0 and cmp >= pos.target_1:
                pos.target_1 = 0.0 # Clear target once hit
                # For T1, close 1/3 of current qty
                return "Target 1 Hit", max(1, pos.qty // 3)
                
            # Fallback legacy target
            if pos.target > 0 and cmp >= pos.target:
                return "Target Hit", pos.qty
                
        else: # SELL
            if cmp >= effective_sl and effective_sl > 0:
                return "SL/Trail Hit", pos.qty
                
            if pos.target_3 > 0 and cmp <= pos.target_3:
                return "Target 3 Hit", pos.qty
                
            if pos.target_2 > 0 and cmp <= pos.target_2:
                pos.target_2 = 0.0
                return "Target 2 Hit", max(1, pos.qty // 2)
                
            if pos.target_1 > 0 and cmp <= pos.target_1:
                pos.target_1 = 0.0
                return "Target 1 Hit", max(1, pos.qty // 3)
                
            if pos.target > 0 and cmp <= pos.target:
                return "Target Hit", pos.qty

        return None, None
