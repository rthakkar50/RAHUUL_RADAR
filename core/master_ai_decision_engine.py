import json
import logging
import csv
import os
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class DecisionAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    WAIT = "WAIT"
    REJECT = "REJECT"

class DecisionGrade(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    FAILED = "FAILED"

class DecisionStatus(str, Enum):
    EXECUTE = "EXECUTE"
    MONITOR = "MONITOR"
    WAIT = "WAIT"
    BLOCKED = "BLOCKED"

@dataclass
class DecisionInput:
    symbol: str
    timestamp: str
    market_regime: str
    false_signal_result: Optional[dict] = None
    mtf_result: Optional[dict] = None
    entry_result: Optional[dict] = None
    exit_result: Optional[dict] = None
    walk_forward_result: Optional[dict] = None
    ranking_result: Optional[dict] = None
    confidence_result: Optional[dict] = None
    performance_result: Optional[dict] = None
    institutional_result: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "market_regime": self.market_regime,
            "false_signal_result": self.false_signal_result,
            "mtf_result": self.mtf_result,
            "entry_result": self.entry_result,
            "exit_result": self.exit_result,
            "walk_forward_result": self.walk_forward_result,
            "ranking_result": self.ranking_result,
            "confidence_result": self.confidence_result,
            "performance_result": self.performance_result,
            "institutional_result": self.institutional_result
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DecisionInput':
        return cls(
            symbol=data.get("symbol", ""),
            timestamp=data.get("timestamp", ""),
            market_regime=data.get("market_regime", ""),
            false_signal_result=data.get("false_signal_result"),
            mtf_result=data.get("mtf_result"),
            entry_result=data.get("entry_result"),
            exit_result=data.get("exit_result"),
            walk_forward_result=data.get("walk_forward_result"),
            ranking_result=data.get("ranking_result"),
            confidence_result=data.get("confidence_result"),
            performance_result=data.get("performance_result"),
            institutional_result=data.get("institutional_result")
        )

@dataclass
class DecisionOutput:
    action: str
    confidence: float
    overall_score: float
    risk_level: float
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    trailing_stop: float
    position_size_factor: float
    decision_grade: str
    decision_status: str
    reason_summary: str
    engine_breakdown: dict
    warnings: List[str]
    execution_time_ms: float

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "confidence": self.confidence,
            "overall_score": self.overall_score,
            "risk_level": self.risk_level,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "target_1": self.target_1,
            "target_2": self.target_2,
            "target_3": self.target_3,
            "trailing_stop": self.trailing_stop,
            "position_size_factor": self.position_size_factor,
            "decision_grade": self.decision_grade,
            "decision_status": self.decision_status,
            "reason_summary": self.reason_summary,
            "engine_breakdown": self.engine_breakdown,
            "warnings": self.warnings,
            "execution_time_ms": self.execution_time_ms
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DecisionOutput':
        return cls(
            action=data.get("action", DecisionAction.REJECT.value),
            confidence=float(data.get("confidence", 0.0)),
            overall_score=float(data.get("overall_score", 0.0)),
            risk_level=float(data.get("risk_level", 0.0)),
            entry_price=float(data.get("entry_price", 0.0)),
            stop_loss=float(data.get("stop_loss", 0.0)),
            target_1=float(data.get("target_1", 0.0)),
            target_2=float(data.get("target_2", 0.0)),
            target_3=float(data.get("target_3", 0.0)),
            trailing_stop=float(data.get("trailing_stop", 0.0)),
            position_size_factor=float(data.get("position_size_factor", 0.0)),
            decision_grade=data.get("decision_grade", DecisionGrade.FAILED.value),
            decision_status=data.get("decision_status", DecisionStatus.BLOCKED.value),
            reason_summary=data.get("reason_summary", ""),
            engine_breakdown=data.get("engine_breakdown", {}),
            warnings=data.get("warnings", []),
            execution_time_ms=float(data.get("execution_time_ms", 0.0))
        )


class MasterAIDecisionEngine:
    def __init__(self, config_path: str = "config/master_ai_rules.json"):
        self.config_path = config_path
        self.validation_thresholds = {}
        self.decision_thresholds = {}
        self.position_size_multipliers = {}
        self.export_settings = {}
        self.load_configuration()

    def load_configuration(self):
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.validation_thresholds = data.get("validation_thresholds", {})
                self.decision_thresholds = data.get("decision_thresholds", {})
                self.position_size_multipliers = data.get("position_size_multipliers", {})
                self.export_settings = data.get("export_settings", {})
        except Exception as e:
            logger.error(f"Failed to load config {self.config_path}: {e}")
            self.validation_thresholds = {
                "minimum_confidence": 75.0, "minimum_institutional_grade": "B",
                "minimum_walk_forward_score": 60.0, "minimum_strategy_rank": 65.0,
                "maximum_risk_level": 5.0
            }
            self.decision_thresholds = {
                "buy_threshold": 80.0, "strong_buy_threshold": 90.0,
                "sell_threshold": 20.0, "strong_sell_threshold": 10.0
            }
            self.position_size_multipliers = {
                "A_PLUS": 1.0, "A": 0.75, "B": 0.5, "C": 0.25, "D": 0.1, "FAILED": 0.0
            }
            self.export_settings = {"default_export_path": "exports/", "enable_pdf_export": True, "enable_csv_export": True}

    def validate_input(self, inputs: DecisionInput) -> (bool, List[str]):
        """Ensure all required module data is present."""
        missing = []
        if inputs.false_signal_result is None: missing.append("false_signal")
        if inputs.mtf_result is None: missing.append("mtf")
        if inputs.entry_result is None: missing.append("entry")
        if inputs.exit_result is None: missing.append("exit")
        if inputs.institutional_result is None: missing.append("institutional")
        if inputs.confidence_result is None: missing.append("confidence")
        
        return len(missing) == 0, missing

    def aggregate_module_results(self, inputs: DecisionInput) -> dict:
        """Extracts key values from all modules."""
        def safe_get(d, key, default):
            return d.get(key, default) if d else default
            
        return {
            "fs_status": safe_get(inputs.false_signal_result, "status", "UNKNOWN"),
            "mtf_score": safe_get(inputs.mtf_result, "score", 50.0),
            "entry_score": safe_get(inputs.entry_result, "entry_score", 50.0),
            "exit_action": safe_get(inputs.exit_result, "exit_action", "HOLD"),
            "wf_score": safe_get(inputs.walk_forward_result, "Validation Score", 50.0),
            "ranking_score": safe_get(inputs.ranking_result, "Composite Score", 50.0),
            "confidence": safe_get(inputs.confidence_result, "confidence", 50.0),
            "perf_status": safe_get(inputs.performance_result, "status", "UNKNOWN"),
            "inst_grade": safe_get(inputs.institutional_result, "institution_grade", "FAILED"),
            "inst_status": safe_get(inputs.institutional_result, "validation_status", "REJECTED"),
            "entry_price": safe_get(inputs.entry_result, "recommended_entry", 0.0),
            "stop_loss": safe_get(inputs.entry_result, "stop_loss", 0.0),
            "target_1": safe_get(inputs.entry_result, "target_1", 0.0),
            "target_2": safe_get(inputs.entry_result, "target_2", 0.0),
            "target_3": safe_get(inputs.entry_result, "target_3", 0.0),
            "trailing_stop": safe_get(inputs.exit_result, "trailing_stop", 0.0)
        }

    def calculate_overall_score(self, aggregated: dict) -> float:
        """Calculates master overall score from core indicator engines."""
        scores = [
            aggregated["mtf_score"],
            aggregated["entry_score"],
            aggregated["wf_score"],
            aggregated["ranking_score"]
        ]
        return max(0.0, min(100.0, sum(scores) / max(len(scores), 1)))

    def calculate_confidence(self, aggregated: dict, missing_modules: List[str]) -> float:
        """Final confidence, applying penalties for missing data."""
        conf = aggregated["confidence"]
        penalty = len(missing_modules) * 10.0
        return max(0.0, min(100.0, conf - penalty))

    def determine_action(self, score: float, aggregated: dict) -> str:
        buy_thr = self.decision_thresholds.get("buy_threshold", 80.0)
        sell_thr = self.decision_thresholds.get("sell_threshold", 20.0)
        
        # Override rules
        if aggregated["fs_status"] == "REJECTED":
            return DecisionAction.REJECT.value
        if aggregated["inst_status"] == "REJECTED":
            return DecisionAction.REJECT.value
            
        if aggregated["exit_action"] == "EXIT":
            return DecisionAction.SELL.value
            
        if score >= buy_thr:
            return DecisionAction.BUY.value
        elif score <= sell_thr:
            return DecisionAction.SELL.value
            
        return DecisionAction.WAIT.value

    def calculate_position_size_factor(self, inst_grade: str) -> float:
        return self.position_size_multipliers.get(inst_grade, 0.0)

    def calculate_risk_level(self, entry_price: float, stop_loss: float) -> float:
        if entry_price > 0 and stop_loss > 0:
            return abs(entry_price - stop_loss) / entry_price * 100.0
        return 0.0

    def generate_engine_breakdown(self, aggregated: dict) -> dict:
        return {
            "False Signal": aggregated["fs_status"],
            "MTF": aggregated["mtf_score"],
            "Entry": aggregated["entry_score"],
            "Exit": aggregated["exit_action"],
            "Confidence": aggregated["confidence"],
            "Institution": aggregated["inst_status"],
            "Performance": aggregated["perf_status"]
        }

    def validate_final_decision(self, action: str, conf: float, risk: float, inst_grade: str) -> (str, List[str]):
        warnings = []
        status = DecisionStatus.EXECUTE.value
        
        min_conf = self.validation_thresholds.get("minimum_confidence", 75.0)
        max_risk = self.validation_thresholds.get("maximum_risk_level", 5.0)
        
        if action == DecisionAction.REJECT.value:
            status = DecisionStatus.BLOCKED.value
            warnings.append("Decision blocked due to critical rejection by upstream modules.")
            
        if conf < min_conf:
            status = DecisionStatus.WAIT.value if status != DecisionStatus.BLOCKED.value else status
            warnings.append(f"Confidence {conf:.1f} below minimum {min_conf}.")
            
        if risk > max_risk:
            status = DecisionStatus.WAIT.value if status != DecisionStatus.BLOCKED.value else status
            warnings.append(f"Risk level {risk:.1f}% exceeds maximum {max_risk}%.")
            
        if inst_grade == "FAILED":
            status = DecisionStatus.BLOCKED.value
            warnings.append("Institution Grade FAILED. Trade inherently blocked.")
            
        return status, warnings

    def generate_reason_summary(self, action: str, status: str, warnings: List[str]) -> str:
        if status == DecisionStatus.BLOCKED.value:
            return f"Trade Blocked: {', '.join(warnings)}"
        elif status == DecisionStatus.WAIT.value:
            return f"Trade Paused: {', '.join(warnings)}"
        elif action == DecisionAction.BUY.value:
            return "Strong technical alignment supporting BUY Execution."
        elif action == DecisionAction.SELL.value:
            return "Strong technical alignment supporting SELL Execution."
        else:
            return "Neutral posture. Awaiting further confirmation."

    def build_decision_report(self, inputs: DecisionInput) -> DecisionOutput:
        start_time = datetime.now()
        logger.info(f"Master AI Decision Started for {inputs.symbol}")
        
        try:
            valid_input, missing = self.validate_input(inputs)
            agg = self.aggregate_module_results(inputs)
            
            score = self.calculate_overall_score(agg)
            conf = self.calculate_confidence(agg, missing)
            
            action = self.determine_action(score, agg)
            risk = self.calculate_risk_level(agg["entry_price"], agg["stop_loss"])
            size = self.calculate_position_size_factor(agg["inst_grade"])
            
            status, warnings = self.validate_final_decision(action, conf, risk, agg["inst_grade"])
            
            if len(missing) > 0:
                warnings.append(f"Missing modules: {', '.join(missing)}")
                
            reason = self.generate_reason_summary(action, status, warnings)
            breakdown = self.generate_engine_breakdown(agg)
            
            # Map grade
            grade = agg["inst_grade"]
            if grade not in [e.value for e in DecisionGrade]:
                grade = DecisionGrade.FAILED.value
                
            if status == DecisionStatus.BLOCKED.value:
                action = DecisionAction.REJECT.value
                size = 0.0
                
            elapsed = (datetime.now() - start_time).total_seconds() * 1000.0
            
            return DecisionOutput(
                action=action,
                confidence=round(conf, 2),
                overall_score=round(score, 2),
                risk_level=round(risk, 2),
                entry_price=agg["entry_price"],
                stop_loss=agg["stop_loss"],
                target_1=agg["target_1"],
                target_2=agg["target_2"],
                target_3=agg["target_3"],
                trailing_stop=agg["trailing_stop"],
                position_size_factor=size,
                decision_grade=grade,
                decision_status=status,
                reason_summary=reason,
                engine_breakdown=breakdown,
                warnings=warnings,
                execution_time_ms=round(elapsed, 2)
            )
            
        except Exception as e:
            logger.error(f"Error during master AI decision: {e}")
            elapsed = (datetime.now() - start_time).total_seconds() * 1000.0
            return DecisionOutput(
                action=DecisionAction.REJECT.value,
                confidence=0.0, overall_score=0.0, risk_level=0.0,
                entry_price=0.0, stop_loss=0.0, target_1=0.0, target_2=0.0, target_3=0.0, trailing_stop=0.0,
                position_size_factor=0.0,
                decision_grade=DecisionGrade.FAILED.value,
                decision_status=DecisionStatus.BLOCKED.value,
                reason_summary=f"Master AI Failure: {str(e)}",
                engine_breakdown={},
                warnings=["System Error"],
                execution_time_ms=round(elapsed, 2)
            )

    def export_decision(self, result: DecisionOutput, format_type: str = "JSON", output_dir: str = None) -> str:
        out_dir = output_dir or self.export_settings.get("default_export_path", "exports/master_ai/")
        os.makedirs(out_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        format_type = format_type.upper()
        
        if format_type == "JSON":
            filepath = os.path.join(out_dir, f"decision_{timestamp}.json")
            with open(filepath, "w") as f:
                json.dump(result.to_dict(), f, indent=4)
        elif format_type == "CSV" and self.export_settings.get("enable_csv_export", True):
            filepath = os.path.join(out_dir, f"decision_{timestamp}.csv")
            with open(filepath, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Key", "Value"])
                for k, v in result.to_dict().items():
                    writer.writerow([k, v])
        elif format_type == "PDF" and self.export_settings.get("enable_pdf_export", True):
            filepath = os.path.join(out_dir, f"decision_{timestamp}.pdf")
            with open(filepath, "w") as f:
                f.write("MOCK PDF EXPORT\n")
                f.write(json.dumps(result.to_dict(), indent=2))
        else:
            raise ValueError(f"Format {format_type} not supported or disabled.")
            
        logger.info(f"Decision export saved to {filepath}")
        return filepath
