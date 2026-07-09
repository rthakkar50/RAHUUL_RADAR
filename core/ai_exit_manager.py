from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class OpenPosition:
    """
    Data container representing an actively managed trade.
    """
    symbol: str
    direction: str
    entry_price: float
    current_price: float
    quantity: int
    entry_time: datetime
    current_pnl: float
    holding_minutes: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "quantity": self.quantity,
            "entry_time": self.entry_time.isoformat() if isinstance(self.entry_time, datetime) else self.entry_time,
            "current_pnl": self.current_pnl,
            "holding_minutes": self.holding_minutes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OpenPosition':
        et = data.get("entry_time")
        if isinstance(et, str):
            try:
                et = datetime.fromisoformat(et)
            except ValueError:
                et = datetime.now()
        
        return cls(
            symbol=data.get("symbol", ""),
            direction=data.get("direction", "BUY"),
            entry_price=float(data.get("entry_price", 0.0)),
            current_price=float(data.get("current_price", 0.0)),
            quantity=int(data.get("quantity", 0)),
            entry_time=et or datetime.now(),
            current_pnl=float(data.get("current_pnl", 0.0)),
            holding_minutes=int(data.get("holding_minutes", 0))
        )

    def __str__(self) -> str:
        return (f"Position: {self.symbol} ({self.direction}) | Entry: {self.entry_price} | "
                f"Current: {self.current_price} | Qty: {self.quantity} | "
                f"PnL: {self.current_pnl:+.2f} | Hold Time: {self.holding_minutes}m")


@dataclass
class ExitDecision:
    """
    Data container for the recommended exit action and trailing stops.
    """
    action: str
    confidence: float
    exit_price: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    trailing_stop: float
    partial_exit_percentage: float
    reason: str

    def __post_init__(self):
        if not (0 <= self.confidence <= 100):
            raise ValueError(f"Confidence must remain between 0 and 100. Got: {self.confidence}")
        if not (0 <= self.partial_exit_percentage <= 100):
            raise ValueError(f"Partial exit percentage must remain between 0 and 100. Got: {self.partial_exit_percentage}")
        
        price_fields = {
            "exit_price": self.exit_price,
            "stop_loss": self.stop_loss,
            "target_1": self.target_1,
            "target_2": self.target_2,
            "target_3": self.target_3,
            "trailing_stop": self.trailing_stop
        }
        for field, value in price_fields.items():
            if value < 0:
                raise ValueError(f"Price field '{field}' must be >= 0. Got: {value}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "confidence": self.confidence,
            "exit_price": self.exit_price,
            "stop_loss": self.stop_loss,
            "target_1": self.target_1,
            "target_2": self.target_2,
            "target_3": self.target_3,
            "trailing_stop": self.trailing_stop,
            "partial_exit_percentage": self.partial_exit_percentage,
            "reason": self.reason
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExitDecision':
        return cls(
            action=data.get("action", "HOLD"),
            confidence=float(data.get("confidence", 0.0)),
            exit_price=float(data.get("exit_price", 0.0)),
            stop_loss=float(data.get("stop_loss", 0.0)),
            target_1=float(data.get("target_1", 0.0)),
            target_2=float(data.get("target_2", 0.0)),
            target_3=float(data.get("target_3", 0.0)),
            trailing_stop=float(data.get("trailing_stop", 0.0)),
            partial_exit_percentage=float(data.get("partial_exit_percentage", 0.0)),
            reason=data.get("reason", "")
        )

    def __str__(self) -> str:
        return (f"Exit Action: {self.action} (Conf: {self.confidence:.1f}%) | Exit: {self.exit_price} | "
                f"SL: {self.stop_loss} | TS: {self.trailing_stop} | "
                f"Targets: ({self.target_1}, {self.target_2}, {self.target_3}) | "
                f"Partial Exit: {self.partial_exit_percentage}% | Reason: {self.reason}")


class AIExitManager:
    """
    Professional Exit Management Engine.
    This engine never creates BUY or SELL signals; it only manages existing trades.
    """
    def __init__(self) -> None:
        pass

    def evaluate_position(self, position: OpenPosition) -> ExitDecision:
        """
        Main orchestration method to evaluate the health and status of an open position.
        Evaluates current Profit/Loss, holding time, trend direction, and current price.
        Returns an ExitDecision containing the action ('CLOSED', 'HOLD', or 'REVIEW') and targets.

        Args:
            position: OpenPosition instance representing the active trade.

        Returns:
            ExitDecision: The structured recommendation output.
        """
        if not position or position.quantity <= 0:
            return ExitDecision(
                action="CLOSED",
                confidence=100.0,
                exit_price=position.current_price if position else 0.0,
                stop_loss=0.0,
                target_1=0.0,
                target_2=0.0,
                target_3=0.0,
                trailing_stop=0.0,
                partial_exit_percentage=0.0,
                reason="Position has zero or negative quantity. Trade is closed."
            )

        direction = position.direction.upper()
        
        # Simple threshold evaluations for decision action
        if position.current_pnl <= -15.0:
            action = "REVIEW"
            reason = f"Position loss ({position.current_pnl:.2f}) exceeds risk threshold."
        elif position.holding_minutes > 120:
            action = "REVIEW"
            reason = f"Position holding time ({position.holding_minutes}m) exceeds timeframe window."
        elif position.current_pnl >= 30.0:
            action = "REVIEW"
            reason = f"Position profit target reached (PnL: {position.current_pnl:.2f})."
        else:
            action = "HOLD"
            reason = "Position performing within normal parameters. No action required."

        # Compute placeholder stop loss, targets, and trailing stop values
        is_buy = direction in ("BUY", "BULL", "BULLISH")
        stop_loss = position.entry_price * 0.95 if is_buy else position.entry_price * 1.05
        t1 = position.entry_price * 1.05 if is_buy else position.entry_price * 0.95
        t2 = position.entry_price * 1.10 if is_buy else position.entry_price * 0.90
        t3 = position.entry_price * 1.15 if is_buy else position.entry_price * 0.85
        trailing_stop = position.current_price * 0.98 if is_buy else position.current_price * 1.02

        return ExitDecision(
            action=action,
            confidence=95.0 if action == "REVIEW" else 100.0,
            exit_price=position.current_price,
            stop_loss=round(max(0.0, stop_loss), 2),
            target_1=round(max(0.0, t1), 2),
            target_2=round(max(0.0, t2), 2),
            target_3=round(max(0.0, t3), 2),
            trailing_stop=round(max(0.0, trailing_stop), 2),
            partial_exit_percentage=0.0,
            reason=reason
        )

    def recommend_exit(self, position: OpenPosition, decision: ExitDecision) -> str:
        """
        Evaluates whether an immediate exit should be triggered based on position metrics.
        Returns one of: 'HOLD', 'PARTIAL_EXIT', 'FULL_EXIT', 'REVIEW'.

        Args:
            position: OpenPosition instance representing the active trade.
            decision: ExitDecision containing preliminary status.

        Returns:
            str: Action recommended ('HOLD', 'PARTIAL_EXIT', 'FULL_EXIT', 'REVIEW').
        """
        if not position or position.quantity <= 0:
            return "HOLD"
            
        if position.current_pnl <= -15.0:
            return "FULL_EXIT"
        elif position.current_pnl >= 30.0:
            return "FULL_EXIT"
        elif 15.0 <= position.current_pnl < 30.0:
            return "PARTIAL_EXIT"
        elif position.holding_minutes > 120:
            return "REVIEW"
            
        return "HOLD"

    def recommend_trailing_stop(self, position: OpenPosition, decision: ExitDecision) -> float:
        """
        Calculates a dynamic trailing stop placeholder without indicator math.
        Ensures the returned stop level is >= 0.

        Args:
            position: OpenPosition instance.
            decision: ExitDecision containing preliminary targets.

        Returns:
            float: Recommended trailing stop level.
        """
        if not position:
            return 0.0
        direction = position.direction.upper()
        is_buy = direction in ("BUY", "BULL", "BULLISH")
        
        # Calculate dynamic trailing stop 2% offset from current price
        offset = position.current_price * 0.02
        ts = position.current_price - offset if is_buy else position.current_price + offset
        return round(max(0.0, ts), 2)

    def recommend_partial_exit(self, position: OpenPosition, decision: ExitDecision) -> float:
        """
        Returns the recommended partial exit percentage (0-100) using placeholder rules.

        Args:
            position: OpenPosition instance.
            decision: ExitDecision containing preliminary targets.

        Returns:
            float: Percentage of position to close (0.0 to 100.0).
        """
        if not position or position.current_pnl < 15.0:
            return 0.0
        
        # Scale exit percentage based on profit milestones
        if 15.0 <= position.current_pnl < 25.0:
            return 30.0
        return 50.0

    def recommend_final_exit(self) -> None:
        """
        Calculates the definitive target or time-based threshold for closing the remainder of the position.
        """
        pass
