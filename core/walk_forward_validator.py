import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ValidationStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"

@dataclass
class ValidationWindow:
    training_start: datetime
    training_end: datetime
    testing_start: datetime
    testing_end: datetime
    window_number: int

    def to_dict(self) -> dict:
        return {
            "training_start": self.training_start.isoformat() if self.training_start else None,
            "training_end": self.training_end.isoformat() if self.training_end else None,
            "testing_start": self.testing_start.isoformat() if self.testing_start else None,
            "testing_end": self.testing_end.isoformat() if self.testing_end else None,
            "window_number": self.window_number
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ValidationWindow':
        return cls(
            training_start=datetime.fromisoformat(data["training_start"]) if data.get("training_start") else None,
            training_end=datetime.fromisoformat(data["training_end"]) if data.get("training_end") else None,
            testing_start=datetime.fromisoformat(data["testing_start"]) if data.get("testing_start") else None,
            testing_end=datetime.fromisoformat(data["testing_end"]) if data.get("testing_end") else None,
            window_number=int(data.get("window_number", 1))
        )

    def __str__(self):
        return f"Window {self.window_number} (Train: {self.training_start.date()} to {self.training_end.date()}, Test: {self.testing_start.date()} to {self.testing_end.date()})"

@dataclass
class TradeResult:
    entry_time: datetime
    exit_time: datetime
    symbol: str
    direction: str
    entry_price: float
    exit_price: float
    quantity: int
    profit_loss: float
    risk_reward: float
    status: str

    def to_dict(self) -> dict:
        return {
            "entry_time": self.entry_time.isoformat() if self.entry_time else None,
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "symbol": self.symbol,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "quantity": self.quantity,
            "profit_loss": self.profit_loss,
            "risk_reward": self.risk_reward,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TradeResult':
        return cls(
            entry_time=datetime.fromisoformat(data["entry_time"]) if data.get("entry_time") else None,
            exit_time=datetime.fromisoformat(data["exit_time"]) if data.get("exit_time") else None,
            symbol=data.get("symbol", "UNKNOWN"),
            direction=data.get("direction", "UNKNOWN"),
            entry_price=float(data.get("entry_price", 0.0)),
            exit_price=float(data.get("exit_price", 0.0)),
            quantity=int(data.get("quantity", 0)),
            profit_loss=float(data.get("profit_loss", 0.0)),
            risk_reward=float(data.get("risk_reward", 0.0)),
            status=data.get("status", "UNKNOWN")
        )

    def __str__(self):
        return f"{self.direction} {self.quantity} {self.symbol} @ {self.entry_price} -> {self.exit_price} PnL: {self.profit_loss}"

@dataclass
class ValidationMetrics:
    strategy_name: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    gross_profit: float
    gross_loss: float
    net_profit: float
    average_rr: float
    maximum_drawdown: float
    expectancy: float
    sharpe_ratio: float
    status: ValidationStatus

    def to_dict(self) -> dict:
        return {
            "strategy_name": self.strategy_name,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "profit_factor": self.profit_factor,
            "gross_profit": self.gross_profit,
            "gross_loss": self.gross_loss,
            "net_profit": self.net_profit,
            "average_rr": self.average_rr,
            "maximum_drawdown": self.maximum_drawdown,
            "expectancy": self.expectancy,
            "sharpe_ratio": self.sharpe_ratio,
            "status": self.status.value
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ValidationMetrics':
        return cls(
            strategy_name=data.get("strategy_name", "UNKNOWN"),
            total_trades=int(data.get("total_trades", 0)),
            winning_trades=int(data.get("winning_trades", 0)),
            losing_trades=int(data.get("losing_trades", 0)),
            win_rate=float(data.get("win_rate", 0.0)),
            profit_factor=float(data.get("profit_factor", 0.0)),
            gross_profit=float(data.get("gross_profit", 0.0)),
            gross_loss=float(data.get("gross_loss", 0.0)),
            net_profit=float(data.get("net_profit", 0.0)),
            average_rr=float(data.get("average_rr", 0.0)),
            maximum_drawdown=float(data.get("maximum_drawdown", 0.0)),
            expectancy=float(data.get("expectancy", 0.0)),
            sharpe_ratio=float(data.get("sharpe_ratio", 0.0)),
            status=ValidationStatus(data.get("status", ValidationStatus.FAILED.value))
        )

    def __str__(self):
        return (f"Strategy: {self.strategy_name} | Status: {self.status.value}\n"
                f"Trades: {self.total_trades} (W: {self.winning_trades} / L: {self.losing_trades}) | Win Rate: {self.win_rate:.2f}%\n"
                f"Profit Factor: {self.profit_factor:.2f} | Net Profit: {self.net_profit:.2f}\n"
                f"Max Drawdown: {self.maximum_drawdown:.2f}% | Expectancy: {self.expectancy:.2f} | Sharpe: {self.sharpe_ratio:.2f}")


class WalkForwardValidator:
    def __init__(self, config_path: str = "config/walk_forward.json"):
        self.config_path = config_path
        self.thresholds = {}
        self.window_settings = {}
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.thresholds = data.get("validation_thresholds", {})
                self.window_settings = data.get("window_settings", {})
        except Exception as e:
            logger.error(f"Failed to load config {self.config_path}: {e}")
            self.thresholds = {
                "minimum_win_rate": 45.0,
                "minimum_profit_factor": 1.5,
                "maximum_drawdown": 20.0,
                "minimum_trades": 30,
                "minimum_expectancy": 0.2,
                "minimum_sharpe_ratio": 1.0
            }
            self.window_settings = {
                "window_size_days": 180,
                "training_split_percentage": 70,
                "testing_split_percentage": 30
            }

    def create_validation_windows(self, start_date: datetime, end_date: datetime) -> List[ValidationWindow]:
        """Creates a list of validation windows based on start and end dates and configured sizes."""
        if start_date >= end_date:
            logger.warning("Start date must be before end date to create windows.")
            return []
            
        import math
        from datetime import timedelta
        
        windows = []
        window_size_days = self.window_settings.get("window_size_days", 180)
        train_pct = self.window_settings.get("training_split_percentage", 70)
        
        train_days = int(window_size_days * (train_pct / 100.0))
        test_days = window_size_days - train_days
        
        current_start = start_date
        window_num = 1
        
        while current_start + timedelta(days=train_days + test_days) <= end_date:
            train_end = current_start + timedelta(days=train_days)
            test_start = train_end
            test_end = test_start + timedelta(days=test_days)
            
            windows.append(ValidationWindow(
                training_start=current_start,
                training_end=train_end,
                testing_start=test_start,
                testing_end=test_end,
                window_number=window_num
            ))
            
            current_start = test_end # Next window starts where previous ends (non-overlapping step)
            window_num += 1
            
        return windows

    def calculate_profit_factor(self, gross_profit: float, gross_loss: float) -> float:
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        return abs(gross_profit / gross_loss)

    def calculate_expectancy(self, win_rate: float, average_win: float, average_loss: float) -> float:
        loss_rate = 100.0 - win_rate
        if average_loss == 0:
            return average_win * (win_rate / 100.0)
        return (average_win * (win_rate / 100.0)) - (abs(average_loss) * (loss_rate / 100.0))

    def calculate_drawdown(self, trades: List[TradeResult]) -> float:
        if not trades:
            return 0.0
        
        peak = 0.0
        max_drawdown = 0.0
        cumulative_pnl = 0.0
        
        for trade in trades:
            cumulative_pnl += trade.profit_loss
            if cumulative_pnl > peak:
                peak = cumulative_pnl
            
            if peak > 0:
                drawdown = ((peak - cumulative_pnl) / peak) * 100.0
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
        
        return max_drawdown

    def calculate_sharpe_ratio(self, trades: List[TradeResult]) -> float:
        if not trades or len(trades) < 2:
            return 0.0
        
        import statistics
        returns = [t.profit_loss for t in trades]
        mean_return = statistics.mean(returns)
        stdev_return = statistics.stdev(returns) if len(returns) > 1 else 0.0
        
        if stdev_return == 0:
            return 0.0
            
        # Assuming risk-free rate is 0 for simplicity
        return mean_return / stdev_return

    def calculate_metrics(self, strategy_name: str, trades: List[TradeResult]) -> ValidationMetrics:
        if not trades:
            return ValidationMetrics(
                strategy_name=strategy_name,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                profit_factor=0.0,
                gross_profit=0.0,
                gross_loss=0.0,
                net_profit=0.0,
                average_rr=0.0,
                maximum_drawdown=0.0,
                expectancy=0.0,
                sharpe_ratio=0.0,
                status=ValidationStatus.FAILED
            )
            
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.profit_loss > 0]
        losing_trades = [t for t in trades if t.profit_loss <= 0]
        
        gross_profit = sum(t.profit_loss for t in winning_trades)
        gross_loss = sum(t.profit_loss for t in losing_trades)
        net_profit = gross_profit + gross_loss
        
        win_rate = (len(winning_trades) / total_trades) * 100.0 if total_trades > 0 else 0.0
        profit_factor = self.calculate_profit_factor(gross_profit, gross_loss)
        
        average_win = gross_profit / len(winning_trades) if winning_trades else 0.0
        average_loss = abs(gross_loss / len(losing_trades)) if losing_trades else 0.0
        
        expectancy = self.calculate_expectancy(win_rate, average_win, average_loss)
        maximum_drawdown = self.calculate_drawdown(trades)
        sharpe_ratio = self.calculate_sharpe_ratio(trades)
        
        rr_list = [t.risk_reward for t in trades if t.risk_reward > 0]
        average_rr = sum(rr_list) / len(rr_list) if rr_list else 0.0
        
        metrics = ValidationMetrics(
            strategy_name=strategy_name,
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            profit_factor=profit_factor,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            net_profit=net_profit,
            average_rr=average_rr,
            maximum_drawdown=maximum_drawdown,
            expectancy=expectancy,
            sharpe_ratio=sharpe_ratio,
            status=ValidationStatus.WARNING # Will be evaluated in validate_strategy
        )
        
        return metrics

    def validate_strategy(self, metrics: ValidationMetrics) -> ValidationStatus:
        if metrics.total_trades == 0:
            metrics.status = ValidationStatus.FAILED
            return metrics.status

        # Read config thresholds
        min_win_rate = self.thresholds.get("minimum_win_rate", 45.0)
        min_pf = self.thresholds.get("minimum_profit_factor", 1.5)
        max_dd = self.thresholds.get("maximum_drawdown", 20.0)
        min_trades = self.thresholds.get("minimum_trades", 30)
        min_exp = self.thresholds.get("minimum_expectancy", 0.2)
        min_sharpe = self.thresholds.get("minimum_sharpe_ratio", 1.0)
        
        fails = []
        warnings = []
        
        if metrics.total_trades < min_trades:
            fails.append("Insufficient trades")
            
        if metrics.win_rate < min_win_rate:
            if metrics.win_rate >= min_win_rate * 0.9:
                warnings.append("Low win rate")
            else:
                fails.append("Failed win rate")
                
        if metrics.profit_factor < min_pf:
            if metrics.profit_factor >= min_pf * 0.9:
                warnings.append("Low profit factor")
            else:
                fails.append("Failed profit factor")
                
        if metrics.maximum_drawdown > max_dd:
            if metrics.maximum_drawdown <= max_dd * 1.2:
                warnings.append("High drawdown")
            else:
                fails.append("Failed max drawdown")
                
        if metrics.expectancy < min_exp:
            if metrics.expectancy > 0:
                warnings.append("Low expectancy")
            else:
                fails.append("Failed expectancy (negative or near zero)")
                
        if metrics.sharpe_ratio < min_sharpe:
            warnings.append("Low sharpe ratio")

        if fails:
            metrics.status = ValidationStatus.FAILED
        elif warnings:
            metrics.status = ValidationStatus.WARNING
        else:
            metrics.status = ValidationStatus.PASSED
            
        return metrics.status

    def run_validation(self, strategy_name: str, trades: List[TradeResult]) -> ValidationMetrics:
        """Runs full validation pipeline for a list of trades."""
        start_time = datetime.now()
        logger.info(f"Validation Start: {strategy_name}")
        
        try:
            metrics = self.calculate_metrics(strategy_name, trades)
            status = self.validate_strategy(metrics)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Validation Complete: {strategy_name} -> {status.value} in {elapsed:.3f}s")
            
            return metrics
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            return ValidationMetrics(
                strategy_name=strategy_name,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                profit_factor=0.0,
                gross_profit=0.0,
                gross_loss=0.0,
                net_profit=0.0,
                average_rr=0.0,
                maximum_drawdown=0.0,
                expectancy=0.0,
                sharpe_ratio=0.0,
                status=ValidationStatus.FAILED
            )

    def generate_validation_report(self, metrics: ValidationMetrics) -> dict:
        """Generates a structured report including Validation Status, Failure Reasons, Recommendations."""
        # Simple evaluation logic for report
        reasons = []
        recommendations = []
        
        if metrics.status == ValidationStatus.FAILED:
            reasons.append("Strategy did not meet minimum robust criteria.")
            if metrics.total_trades < self.thresholds.get("minimum_trades", 30):
                reasons.append("Trade count too low.")
                recommendations.append("Extend backtest period.")
            if metrics.profit_factor < self.thresholds.get("minimum_profit_factor", 1.5):
                reasons.append(f"Profit factor {metrics.profit_factor:.2f} is below minimum.")
                recommendations.append("Improve exit logic or increase win rate.")
        elif metrics.status == ValidationStatus.WARNING:
            reasons.append("Strategy met some but not all robust criteria.")
            recommendations.append("Proceed with caution. Consider position sizing reduction.")
        else:
            reasons.append("Strategy passed all criteria.")
            recommendations.append("Strategy is robust enough for production deployment.")
            
        return {
            "Strategy Name": metrics.strategy_name,
            "Validation Status": metrics.status.value,
            "Performance Metrics": {
                "Total Trades": metrics.total_trades,
                "Win Rate (%)": f"{metrics.win_rate:.2f}",
                "Profit Factor": f"{metrics.profit_factor:.2f}",
                "Net Profit": f"{metrics.net_profit:.2f}",
                "Expectancy": f"{metrics.expectancy:.2f}"
            },
            "Risk Metrics": {
                "Max Drawdown (%)": f"{metrics.maximum_drawdown:.2f}",
                "Sharpe Ratio": f"{metrics.sharpe_ratio:.2f}",
                "Average RR": f"{metrics.average_rr:.2f}"
            },
            "Failure Reasons": reasons,
            "Recommendations": recommendations
        }
