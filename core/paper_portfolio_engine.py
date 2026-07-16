import logging
import uuid
from datetime import datetime
from typing import Dict, Optional, Tuple, List

from core.models.paper_portfolio_models import PaperPosition, PaperPortfolioState

logger = logging.getLogger("PaperPortfolioEngine")

class PaperPortfolioEngine:
    """
    Core engine responsible for maintaining paper trading portfolio state,
    calculating MTM (Mark-to-Market), and managing virtual capital.
    """
    
    def __init__(self, starting_capital: float = 1000000.0, max_open_positions: int = 5, max_risk_per_trade_pct: float = 1.0, max_exposure_pct: float = 80.0):
        self.starting_capital = starting_capital
        self.max_open_positions = max_open_positions
        self.max_risk_per_trade_pct = max_risk_per_trade_pct
        self.max_exposure_pct = max_exposure_pct
        
        self.virtual_capital = starting_capital
        self.available_cash = starting_capital
        self.used_margin = 0.0
        self.realized_pnl = 0.0
        
        self.open_positions: Dict[str, PaperPosition] = {}
        self.closed_positions = []
        
        # Integrate Position Manager
        from core.paper_position_manager import PaperPositionManager
        self.position_manager = PaperPositionManager(self)
        
    def execute_trade(self, symbol: str, direction: str, price: float, sl: float, target: float) -> Tuple[bool, Optional[str], str]:
        """
        Executes a paper trade if risk and exposure limits allow.
        Returns: (success, position_id, message)
        """
        if len(self.open_positions) >= self.max_open_positions:
            return False, None, "Risk Rejected: Max open positions reached."
            
        # Position Sizing
        risk_amount = self.virtual_capital * (self.max_risk_per_trade_pct / 100.0)
        price_risk = abs(price - sl)
        if price_risk <= 0:
            price_risk = price * 0.01  # Fallback 1% risk
            
        qty = int(risk_amount / price_risk)
        if qty <= 0:
            qty = 1
            
        trade_val = qty * price
        
        # Exposure Check
        if (self.used_margin + trade_val) > (self.virtual_capital * (self.max_exposure_pct / 100.0)):
            return False, None, "Risk Rejected: Max exposure limit exceeded."
            
        pos_id = str(uuid.uuid4())[:8]
        charges = self.calculate_charges(qty, price)
        
        position = PaperPosition(
            position_id=pos_id,
            symbol=symbol,
            direction=direction,
            qty=qty,
            entry_price=price,
            current_price=price,
            sl=sl,
            target=target,
            unrealized_pnl=0.0,
            used_margin=trade_val,
            charges=charges
        )
        
        self.open_positions[pos_id] = position
        
        # Update capital & margin
        self.available_cash -= (trade_val + charges)
        self.used_margin += trade_val
        self.virtual_capital -= charges  # Charges immediately hit equity
        self.realized_pnl -= charges
        
        return True, pos_id, f"Order Executed: {direction} {qty} {symbol} @ {price}"

    def update_market_prices(self, prices_dict: Dict[str, float]) -> Tuple[PaperPortfolioState, List]:
        """
        Updates the MTM for open positions based on current market prices.
        Then delegates exit condition evaluation to PaperPositionManager.
        """
        for pid, pos in self.open_positions.items():
            if pos.symbol in prices_dict:
                cmp = prices_dict[pos.symbol]
                pos.current_price = cmp
                
                if pos.direction == 'BUY':
                    pos.unrealized_pnl = (cmp - pos.entry_price) * pos.qty
                else:
                    pos.unrealized_pnl = (pos.entry_price - cmp) * pos.qty
                    
        # Evaluate for exits
        exits = self.position_manager.evaluate_positions(prices_dict)
        for pid, cmp, reason, close_qty in exits:
            self.close_position(pid, cmp, reason, close_qty)
            
        return self.get_portfolio_state(), exits
        
    def close_position(self, pos_id: str, exit_price: float, reason: str = "Manual", close_qty: Optional[int] = None):
        """
        Closes an open position and realizes the PnL.
        If close_qty is provided and is less than pos.qty, a partial exit is performed.
        """
        if pos_id in self.open_positions:
            pos = self.open_positions[pos_id]
            
            # Determine how much to close
            if close_qty is None or close_qty >= pos.qty:
                actual_close_qty = pos.qty
                is_partial = False
            else:
                actual_close_qty = close_qty
                is_partial = True
                
            pos.exit_price = exit_price
            pos.exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if pos.direction == 'BUY':
                gross_pnl = (exit_price - pos.entry_price) * actual_close_qty
            else:
                gross_pnl = (pos.entry_price - exit_price) * actual_close_qty
                
            exit_charges = self.calculate_charges(actual_close_qty, exit_price)
            realized_trade_pnl = gross_pnl - exit_charges
            pos.charges += exit_charges
            pos.realized_pnl += realized_trade_pnl
            
            # Release Margin Proportionally
            released_margin = (actual_close_qty / pos.qty) * pos.used_margin
            
            # State adjustments
            self.realized_pnl += realized_trade_pnl
            self.virtual_capital += realized_trade_pnl
            self.used_margin -= released_margin
            self.available_cash += (released_margin + realized_trade_pnl)
            
            if not is_partial:
                pos.status = 'CLOSED'
                self.closed_positions.append(pos)
                del self.open_positions[pos_id]
                logger.info(f"Position Closed: {pos.symbol} ({reason}) | PNL: {realized_trade_pnl:.2f}")
            else:
                pos.qty -= actual_close_qty
                pos.used_margin -= released_margin
                logger.info(f"Partial Exit: {pos.symbol} ({reason}) | Qty: {actual_close_qty} | PNL: {realized_trade_pnl:.2f}")

    def get_portfolio_state(self) -> PaperPortfolioState:
        """
        Calculates and returns the current state of the paper portfolio.
        """
        total_unrealized = sum(p.unrealized_pnl for p in self.open_positions.values())
        total_equity = self.virtual_capital + total_unrealized
        
        return PaperPortfolioState(
            virtual_capital=self.virtual_capital,
            available_cash=self.available_cash,
            used_margin=self.used_margin,
            realized_pnl=self.realized_pnl,
            unrealized_pnl=total_unrealized,
            total_equity=total_equity,
            open_positions=dict(self.open_positions),
            closed_positions=list(self.closed_positions)
        )

    def calculate_charges(self, qty: int, price: float) -> float:
        """
        Approximate Indian Equity Charges for Paper Trading.
        """
        turnover = qty * price
        brokerage = min(20, turnover * 0.0003)
        stt = turnover * 0.00025
        exchange = turnover * 0.0000345
        gst = (brokerage + exchange) * 0.18
        sebi = turnover * 0.000001
        stamp = turnover * 0.00003
        return brokerage + stt + exchange + gst + sebi + stamp
