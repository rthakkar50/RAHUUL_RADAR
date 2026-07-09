import uuid
from datetime import datetime
from typing import Optional, Callable
from .models import TradeEntry, JournalStats
from .storage import JournalStorage
from .statistics_engine import StatisticsEngine

class JournalManager:
    def __init__(self, db_path: str = "database/journal.db"):
        self.storage = JournalStorage(db_path)
        self.screenshot_callback: Optional[Callable[[str], str]] = None
        
    def set_screenshot_callback(self, callback: Callable[[str], str]):
        """
        Registers a hook to capture the screen. The callback should take a trade_id 
        and return the absolute path to the saved screenshot image.
        """
        self.screenshot_callback = callback
        
    def log_trade(
        self,
        symbol: str,
        entry_price: float,
        exit_price: float,
        stop_loss: float,
        target: float,
        risk_amount: float,
        pnl: float,
        emotion_notes: str = "",
        ai_notes: str = ""
    ) -> TradeEntry:
        trade_id = str(uuid.uuid4())
        
        # Calculate Realized RR
        risk = entry_price - stop_loss
        reward = exit_price - entry_price if pnl > 0 else entry_price - exit_price
        
        realized_rr = 0.0
        if risk != 0:
            realized_rr = round(abs(pnl / risk_amount), 2) if risk_amount > 0 else 0.0
            if pnl < 0:
                realized_rr = -realized_rr
                
        # Capture Screenshot if UI hook is provided
        screenshot_path = None
        if self.screenshot_callback:
            try:
                screenshot_path = self.screenshot_callback(trade_id)
            except Exception as e:
                print(f"Failed to capture screenshot: {e}")
                
        entry = TradeEntry(
            trade_id=trade_id,
            symbol=symbol,
            entry_price=entry_price,
            exit_price=exit_price,
            stop_loss=stop_loss,
            target=target,
            risk_amount=risk_amount,
            realized_rr=realized_rr,
            pnl=pnl,
            screenshot_path=screenshot_path,
            emotion_notes=emotion_notes,
            ai_notes=ai_notes,
            timestamp=datetime.now()
        )
        
        self.storage.save_trade(entry)
        return entry
        
    def get_statistics(self) -> JournalStats:
        trades = self.storage.get_all_trades()
        return StatisticsEngine.calculate_stats(trades)
        
    def generate_monthly_report(self) -> dict:
        # In a full implementation, this would group by month
        stats = self.get_statistics()
        return {
            "Total Trades": stats.total_trades,
            "Win Rate": f"{stats.win_rate}%",
            "Average RR": stats.average_rr,
            "Profit Factor": stats.profit_factor,
            "Max Drawdown": stats.max_drawdown,
            "Net PnL": stats.net_pnl
        }
