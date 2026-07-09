import json
import logging
import csv
import os
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ExecutionMode(str, Enum):
    PAPER = "PAPER"
    SIMULATION = "SIMULATION"
    BROKER_READY = "BROKER_READY"

class ExecutionStatus(str, Enum):
    QUEUED = "QUEUED"
    VALIDATED = "VALIDATED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

@dataclass
class ExecutionRequest:
    symbol: str
    action: str
    quantity: int
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    confidence: float
    position_size_factor: float
    strategy_name: str
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "action": self.action,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "target_1": self.target_1,
            "target_2": self.target_2,
            "target_3": self.target_3,
            "confidence": self.confidence,
            "position_size_factor": self.position_size_factor,
            "strategy_name": self.strategy_name,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ExecutionRequest':
        return cls(
            symbol=data.get("symbol", ""),
            action=data.get("action", ""),
            quantity=int(data.get("quantity", 0)),
            entry_price=float(data.get("entry_price", 0.0)),
            stop_loss=float(data.get("stop_loss", 0.0)),
            target_1=float(data.get("target_1", 0.0)),
            target_2=float(data.get("target_2", 0.0)),
            target_3=float(data.get("target_3", 0.0)),
            confidence=float(data.get("confidence", 0.0)),
            position_size_factor=float(data.get("position_size_factor", 0.0)),
            strategy_name=data.get("strategy_name", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat())
        )

@dataclass
class ExecutionResult:
    execution_id: str
    status: str
    message: str
    execution_time: str
    mode: str
    risk_check: bool
    validation_check: bool
    paper_trade_id: str
    broker_order_reference: str
    warnings: List[str]

    def to_dict(self) -> dict:
        return {
            "execution_id": self.execution_id,
            "status": self.status,
            "message": self.message,
            "execution_time": self.execution_time,
            "mode": self.mode,
            "risk_check": self.risk_check,
            "validation_check": self.validation_check,
            "paper_trade_id": self.paper_trade_id,
            "broker_order_reference": self.broker_order_reference,
            "warnings": self.warnings
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ExecutionResult':
        return cls(
            execution_id=data.get("execution_id", ""),
            status=data.get("status", ExecutionStatus.FAILED.value),
            message=data.get("message", ""),
            execution_time=data.get("execution_time", ""),
            mode=data.get("mode", ExecutionMode.PAPER.value),
            risk_check=bool(data.get("risk_check", False)),
            validation_check=bool(data.get("validation_check", False)),
            paper_trade_id=data.get("paper_trade_id", ""),
            broker_order_reference=data.get("broker_order_reference", ""),
            warnings=data.get("warnings", [])
        )

class AbstractExecutionAdapter(ABC):
    @abstractmethod
    def place_order(self, request: ExecutionRequest) -> dict:
        pass
    
    @abstractmethod
    def modify_order(self, order_id: str, updates: dict) -> dict:
        pass
        
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        pass


class TradeExecutionCenter:
    def __init__(self, config_path: str = "config/trade_execution_rules.json"):
        self.config_path = config_path
        self.execution_settings = {}
        self.risk_limits = {}
        self.simulation_settings = {}
        self.export_settings = {}
        self.queue = []
        self.adapters = {} # Hook for future AbstractExecutionAdapter instances
        self.load_configuration()

    def load_configuration(self):
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.execution_settings = data.get("execution_settings", {})
                self.risk_limits = data.get("risk_limits", {})
                self.simulation_settings = data.get("simulation_settings", {})
                self.export_settings = data.get("export_settings", {})
        except Exception as e:
            logger.error(f"Failed to load config {self.config_path}: {e}")
            self.execution_settings = {
                "default_mode": "PAPER", "maximum_position_size": 1000,
                "maximum_concurrent_trades": 10, "execution_timeout_ms": 5000,
                "max_queue_size": 50
            }
            self.risk_limits = {
                "maximum_risk_per_trade_pct": 2.0, "maximum_slippage_pct": 0.5,
                "minimum_confidence_to_execute": 75.0
            }
            self.simulation_settings = {
                "default_slippage_pct": 0.1, "default_commission_pct": 0.05,
                "simulated_latency_ms": 50
            }
            self.export_settings = {"default_export_path": "exports/", "enable_pdf_export": True, "enable_csv_export": True}

    def validate_request(self, req: ExecutionRequest) -> (bool, List[str]):
        errors = []
        if not req.symbol: errors.append("Missing symbol")
        if not req.action or req.action not in ["BUY", "SELL"]: errors.append("Missing or invalid action")
        if req.quantity <= 0: errors.append("Invalid quantity")
        if req.entry_price <= 0: errors.append("Invalid entry price")
        if req.confidence < 0 or req.confidence > 100: errors.append("Invalid confidence")
        if req.action == "BUY" and req.stop_loss >= req.entry_price: errors.append("Invalid stop loss for BUY")
        if req.action == "SELL" and req.stop_loss > 0 and req.stop_loss <= req.entry_price: errors.append("Invalid stop loss for SELL")
        return len(errors) == 0, errors

    def perform_risk_check(self, req: ExecutionRequest) -> (bool, str):
        if req.quantity > self.execution_settings.get("maximum_position_size", 1000):
            return False, "Position size exceeds maximum limit."
            
        risk_pct = 0.0
        if req.entry_price > 0 and req.stop_loss > 0:
            risk_pct = abs(req.entry_price - req.stop_loss) / req.entry_price * 100.0
            
        if risk_pct > self.risk_limits.get("maximum_risk_per_trade_pct", 2.0):
            return False, f"Risk {risk_pct:.2f}% exceeds limit."
            
        return True, "Risk check passed."

    def perform_validation_check(self, req: ExecutionRequest) -> (bool, str):
        min_conf = self.risk_limits.get("minimum_confidence_to_execute", 75.0)
        if req.confidence < min_conf:
            return False, f"Confidence {req.confidence} below threshold {min_conf}."
        return True, "Institutional validation check passed."

    def queue_execution(self, req: ExecutionRequest) -> str:
        """Enqueues the request. Supports FIFO constraints."""
        max_q = self.execution_settings.get("max_queue_size", 50)
        if len(self.queue) >= max_q:
            raise OverflowError("Execution queue is full.")
            
        exec_id = str(uuid.uuid4())
        self.queue.append({
            "id": exec_id,
            "request": req,
            "status": ExecutionStatus.QUEUED.value,
            "enqueued_at": datetime.now()
        })
        logger.info(f"Execution {exec_id} queued.")
        return exec_id

    def cancel_execution(self, exec_id: str) -> bool:
        """Removes from queue if not executed."""
        for item in self.queue:
            if item["id"] == exec_id and item["status"] == ExecutionStatus.QUEUED.value:
                item["status"] = ExecutionStatus.CANCELLED.value
                logger.info(f"Execution {exec_id} cancelled.")
                return True
        return False

    def prepare_execution(self, req: ExecutionRequest) -> ExecutionResult:
        """Runs the validation and risk pipeline before actual routing."""
        exec_id = self.queue_execution(req)
        
        # Simulating FIFO processing immediately for this implementation
        valid, errs = self.validate_request(req)
        if not valid:
            return self._finalize_exec(exec_id, ExecutionStatus.REJECTED, f"Validation Failed: {errs}")
            
        risk_pass, risk_msg = self.perform_risk_check(req)
        if not risk_pass:
            return self._finalize_exec(exec_id, ExecutionStatus.REJECTED, risk_msg)
            
        val_pass, val_msg = self.perform_validation_check(req)
        if not val_pass:
            return self._finalize_exec(exec_id, ExecutionStatus.REJECTED, val_msg)
            
        return self._finalize_exec(exec_id, ExecutionStatus.VALIDATED, "Ready for routing.", risk_pass, val_pass)

    def _finalize_exec(self, exec_id: str, status: ExecutionStatus, msg: str, risk_check=False, val_check=False) -> ExecutionResult:
        # Update queue status
        req = None
        for item in self.queue:
            if item["id"] == exec_id:
                item["status"] = status.value
                req = item["request"]
                break
                
        mode = self.execution_settings.get("default_mode", ExecutionMode.PAPER.value)
        
        return ExecutionResult(
            execution_id=exec_id,
            status=status.value,
            message=msg,
            execution_time=datetime.now().isoformat(),
            mode=mode,
            risk_check=risk_check,
            validation_check=val_check,
            paper_trade_id="",
            broker_order_reference="",
            warnings=[]
        )

    def execute_paper_trade(self, req: ExecutionRequest) -> ExecutionResult:
        res = self.prepare_execution(req)
        if res.status != ExecutionStatus.VALIDATED.value:
            return res
            
        # Simulate paper trade
        res.status = ExecutionStatus.EXECUTED.value
        res.mode = ExecutionMode.PAPER.value
        res.paper_trade_id = f"PT_{uuid.uuid4().hex[:8].upper()}"
        res.message = "Paper trade executed successfully."
        
        # --- TLE HOOK ---
        from core.trade_lifecycle_engine import TradeLifecycleEngine
        tle = TradeLifecycleEngine()
        trade_data = req.to_dict()
        trade_data["Signal"] = trade_data["action"]
        trade_data["Entry"] = trade_data["entry_price"]
        trade_data["Stop Loss"] = trade_data["stop_loss"]
        trade_data["Target 1"] = trade_data["target_1"]
        trade_data["Target 2"] = trade_data["target_2"]
        trade_id = tle.create_signal(trade_data)
        tle.trigger_entry(trade_id, req.entry_price, slippage=0.0)
        
        return res

    def execute_simulation(self, req: ExecutionRequest) -> ExecutionResult:
        res = self.prepare_execution(req)
        if res.status != ExecutionStatus.VALIDATED.value:
            return res
            
        slip = self.simulation_settings.get("default_slippage_pct", 0.1)
        sim_price = req.entry_price * (1 + (slip/100.0) if req.action == "BUY" else 1 - (slip/100.0))
        
        res.status = ExecutionStatus.EXECUTED.value
        res.mode = ExecutionMode.SIMULATION.value
        res.message = f"Simulation executed with {slip}% slippage at {sim_price:.2f}"
        res.warnings.append(f"Applied slippage: {slip}%")
        
        # --- TLE HOOK ---
        from core.trade_lifecycle_engine import TradeLifecycleEngine
        tle = TradeLifecycleEngine()
        trade_data = req.to_dict()
        trade_data["Signal"] = trade_data["action"]
        trade_data["Entry"] = trade_data["entry_price"]
        trade_data["Stop Loss"] = trade_data["stop_loss"]
        trade_data["Target 1"] = trade_data["target_1"]
        trade_data["Target 2"] = trade_data["target_2"]
        trade_id = tle.create_signal(trade_data)
        tle.trigger_entry(trade_id, req.entry_price, slippage=slip/100.0)
        
        return res

    def generate_execution_report(self, result: ExecutionResult, req: ExecutionRequest) -> dict:
        return {
            "Execution ID": result.execution_id,
            "Symbol": req.symbol,
            "Action": req.action,
            "Quantity": req.quantity,
            "Status": result.status,
            "Mode": result.mode,
            "Message": result.message,
            "Risk Checked": result.risk_check,
            "Validation Checked": result.validation_check,
            "Warnings": result.warnings
        }

    def export_execution(self, result: ExecutionResult, format_type: str = "JSON", output_dir: str = None) -> str:
        out_dir = output_dir or self.export_settings.get("default_export_path", "exports/executions/")
        os.makedirs(out_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        format_type = format_type.upper()
        
        if format_type == "JSON":
            filepath = os.path.join(out_dir, f"execution_{timestamp}.json")
            with open(filepath, "w") as f:
                json.dump(result.to_dict(), f, indent=4)
        elif format_type == "CSV" and self.export_settings.get("enable_csv_export", True):
            filepath = os.path.join(out_dir, f"execution_{timestamp}.csv")
            with open(filepath, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Key", "Value"])
                for k, v in result.to_dict().items():
                    writer.writerow([k, str(v)])
        elif format_type == "PDF" and self.export_settings.get("enable_pdf_export", True):
            filepath = os.path.join(out_dir, f"execution_{timestamp}.pdf")
            with open(filepath, "w") as f:
                f.write("MOCK PDF EXPORT\n")
                f.write(json.dumps(result.to_dict(), indent=2))
        else:
            raise ValueError(f"Format {format_type} not supported or disabled.")
            
        logger.info(f"Execution report exported to {filepath}")
        return filepath
