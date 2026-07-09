import json
import logging
import csv
import os
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class InstitutionGrade(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    FAILED = "FAILED"

class ValidationStatus(str, Enum):
    APPROVED = "APPROVED"
    CONDITIONAL = "CONDITIONAL"
    REJECTED = "REJECTED"

@dataclass
class InstitutionalValidationInput:
    false_signal_result: Optional[dict] = None
    mtf_result: Optional[dict] = None
    entry_result: Optional[dict] = None
    exit_result: Optional[dict] = None
    walk_forward_result: Optional[dict] = None
    ranking_result: Optional[dict] = None
    confidence_result: Optional[dict] = None
    performance_result: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "false_signal_result": self.false_signal_result,
            "mtf_result": self.mtf_result,
            "entry_result": self.entry_result,
            "exit_result": self.exit_result,
            "walk_forward_result": self.walk_forward_result,
            "ranking_result": self.ranking_result,
            "confidence_result": self.confidence_result,
            "performance_result": self.performance_result
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'InstitutionalValidationInput':
        return cls(
            false_signal_result=data.get("false_signal_result", {}),
            mtf_result=data.get("mtf_result", {}),
            entry_result=data.get("entry_result", {}),
            exit_result=data.get("exit_result", {}),
            walk_forward_result=data.get("walk_forward_result", {}),
            ranking_result=data.get("ranking_result", {}),
            confidence_result=data.get("confidence_result", {}),
            performance_result=data.get("performance_result", {})
        )

@dataclass
class InstitutionalValidationResult:
    approved: bool
    overall_score: float
    institution_grade: str
    validation_status: str
    warnings: List[str]
    failed_modules: List[str]
    recommendations: List[str]
    execution_time_ms: float

    def to_dict(self) -> dict:
        return {
            "approved": self.approved,
            "overall_score": self.overall_score,
            "institution_grade": self.institution_grade,
            "validation_status": self.validation_status,
            "warnings": self.warnings,
            "failed_modules": self.failed_modules,
            "recommendations": self.recommendations,
            "execution_time_ms": self.execution_time_ms
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'InstitutionalValidationResult':
        return cls(
            approved=bool(data.get("approved", False)),
            overall_score=float(data.get("overall_score", 0.0)),
            institution_grade=data.get("institution_grade", InstitutionGrade.FAILED.value),
            validation_status=data.get("validation_status", ValidationStatus.REJECTED.value),
            warnings=data.get("warnings", []),
            failed_modules=data.get("failed_modules", []),
            recommendations=data.get("recommendations", []),
            execution_time_ms=float(data.get("execution_time_ms", 0.0))
        )


class InstitutionalValidationEngine:
    def __init__(self, config_path: str = "config/institutional_validation.json"):
        self.config_path = config_path
        self.thresholds = {}
        self.grade_thresholds = {}
        self.module_weights = {}
        self.export_settings = {}
        self.load_configuration()

    def load_configuration(self):
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.thresholds = data.get("validation_thresholds", {})
                self.grade_thresholds = data.get("grade_thresholds", {})
                self.module_weights = data.get("module_weights", {})
                self.export_settings = data.get("export_settings", {})
        except Exception as e:
            logger.error(f"Failed to load config {self.config_path}: {e}")
            self.thresholds = {
                "minimum_overall_score": 75.0,
                "minimum_confidence": 70.0,
                "minimum_walk_forward_score": 60.0,
                "minimum_ranking_score": 65.0,
                "minimum_performance_score": 50.0,
                "maximum_drawdown_pct": 20.0
            }
            self.grade_thresholds = {"A_PLUS": 95.0, "A": 85.0, "B": 75.0, "C": 65.0, "D": 50.0}
            self.module_weights = {
                "false_signal_weight": 0.20, "mtf_weight": 0.10, "entry_weight": 0.15,
                "exit_weight": 0.10, "walk_forward_weight": 0.15, "ranking_weight": 0.10,
                "confidence_weight": 0.15, "performance_weight": 0.05
            }
            self.export_settings = {"default_export_path": "exports/", "enable_pdf_export": True, "enable_csv_export": True}

    def validate_input(self, inputs: InstitutionalValidationInput) -> (bool, List[str]):
        """Ensure inputs structure is valid."""
        missing = []
        if inputs.false_signal_result is None: missing.append("False Signal")
        if inputs.walk_forward_result is None: missing.append("Walk Forward")
        # Just simple existence checks since we gracefully handle missing data below
        return len(missing) == 0, missing

    def validate_all_modules(self, inputs: InstitutionalValidationInput) -> (bool, List[str], List[str], dict):
        warnings = []
        failed = []
        scores = {}
        
        # False Signal
        fs = inputs.false_signal_result or {}
        fs_status = fs.get("status", "APPROVED")
        if fs_status == "REJECTED":
            failed.append("FalseSignalDetector")
        scores["false_signal"] = 100.0 if fs_status != "REJECTED" else 0.0

        # Confidence
        conf = inputs.confidence_result or {}
        c_score = conf.get("confidence", 0.0)
        c_status = conf.get("status", "REJECTED")
        if c_score < self.thresholds.get("minimum_confidence", 70.0) or c_status == "REJECTED":
            failed.append("ConfidenceCalibration")
        scores["confidence"] = c_score

        # Walk Forward
        wf = inputs.walk_forward_result or {}
        wf_score = wf.get("Validation Score", 0.0)
        wf_dd = wf.get("Metrics", {}).get("Max Drawdown (%)", 0.0)
        if wf_score < self.thresholds.get("minimum_walk_forward_score", 60.0):
            failed.append("WalkForwardValidator (Score)")
        if wf_dd > self.thresholds.get("maximum_drawdown_pct", 20.0):
            failed.append("WalkForwardValidator (Drawdown)")
        scores["walk_forward"] = wf_score

        # Strategy Ranking
        rnk = inputs.ranking_result or {}
        rnk_score = rnk.get("Composite Score", 0.0)
        if rnk_score < self.thresholds.get("minimum_ranking_score", 65.0):
            failed.append("StrategyRankingEngine")
        scores["ranking"] = rnk_score
        
        # Performance
        perf = inputs.performance_result or {}
        p_status = perf.get("status", "GOOD")
        p_score = perf.get("metrics", {}).get("optimization_score", 100.0)
        if p_status == "CRITICAL" or p_score < self.thresholds.get("minimum_performance_score", 50.0):
            failed.append("PerformanceOptimizer")
        scores["performance"] = p_score

        # MTF, Entry, Exit - generic extraction
        mtf = inputs.mtf_result or {}
        if mtf.get("status") == "REJECTED": failed.append("MultiTimeframe")
        scores["mtf"] = float(mtf.get("score", 100.0))
        
        ent = inputs.entry_result or {}
        scores["entry"] = float(ent.get("entry_score", 100.0))
        
        ext = inputs.exit_result or {}
        scores["exit"] = float(ext.get("exit_confidence", 100.0))

        if failed:
            warnings.append(f"Critical module failures: {', '.join(failed)}")

        return (len(failed) == 0), warnings, failed, scores

    def calculate_overall_score(self, scores: dict) -> float:
        w = self.module_weights
        total = (
            scores.get("false_signal", 0.0) * w.get("false_signal_weight", 0.20) +
            scores.get("mtf", 0.0) * w.get("mtf_weight", 0.10) +
            scores.get("entry", 0.0) * w.get("entry_weight", 0.15) +
            scores.get("exit", 0.0) * w.get("exit_weight", 0.10) +
            scores.get("walk_forward", 0.0) * w.get("walk_forward_weight", 0.15) +
            scores.get("ranking", 0.0) * w.get("ranking_weight", 0.10) +
            scores.get("confidence", 0.0) * w.get("confidence_weight", 0.15) +
            scores.get("performance", 0.0) * w.get("performance_weight", 0.05)
        )
        # Normalize in case weights don't sum exactly to 1.0
        weight_sum = sum(w.values())
        if weight_sum > 0:
            total /= weight_sum
            
        return max(0.0, min(100.0, total))

    def calculate_institution_grade(self, score: float) -> str:
        if score >= self.grade_thresholds.get("A_PLUS", 95.0): return InstitutionGrade.A_PLUS.value
        if score >= self.grade_thresholds.get("A", 85.0): return InstitutionGrade.A.value
        if score >= self.grade_thresholds.get("B", 75.0): return InstitutionGrade.B.value
        if score >= self.grade_thresholds.get("C", 65.0): return InstitutionGrade.C.value
        if score >= self.grade_thresholds.get("D", 50.0): return InstitutionGrade.D.value
        return InstitutionGrade.FAILED.value

    def generate_recommendations(self, status: str, grade: str) -> List[str]:
        recs = []
        if status == ValidationStatus.REJECTED.value:
            recs.append("DO NOT EXECUTE. Trade violates critical institutional policies.")
        elif status == ValidationStatus.CONDITIONAL.value:
            recs.append("EXECUTE WITH CAUTION. Halve position size. Closely monitor drawdown.")
        else:
            if grade in [InstitutionGrade.A_PLUS.value, InstitutionGrade.A.value]:
                recs.append("EXECUTE WITH FULL CONFIDENCE. Institutional quality signal.")
            else:
                recs.append("EXECUTE. Standard risk management applies.")
        return recs

    def build_validation_report(self, inputs: InstitutionalValidationInput) -> InstitutionalValidationResult:
        start_time = datetime.now()
        logger.info("Institutional Validation Started")
        
        try:
            valid_input, init_missing = self.validate_input(inputs)
            all_passed, warnings, failed, scores = self.validate_all_modules(inputs)
            
            if init_missing:
                warnings.append(f"Missing input modules: {', '.join(init_missing)}")
                
            overall_score = self.calculate_overall_score(scores)
            grade = self.calculate_institution_grade(overall_score)
            
            if not all_passed:
                status = ValidationStatus.REJECTED.value
                grade = InstitutionGrade.FAILED.value
                approved = False
            else:
                min_overall = self.thresholds.get("minimum_overall_score", 75.0)
                if overall_score >= min_overall:
                    status = ValidationStatus.APPROVED.value
                    approved = True
                elif overall_score >= min_overall - 10.0:
                    status = ValidationStatus.CONDITIONAL.value
                    warnings.append(f"Score {overall_score:.2f} is below target {min_overall} but within conditional range.")
                    approved = True
                else:
                    status = ValidationStatus.REJECTED.value
                    grade = InstitutionGrade.FAILED.value
                    warnings.append(f"Overall score {overall_score:.2f} too low (Min: {min_overall}).")
                    approved = False
                    
            recs = self.generate_recommendations(status, grade)
            
            elapsed = (datetime.now() - start_time).total_seconds() * 1000.0
            logger.info(f"Institutional Validation Completed in {elapsed:.2f}ms. Status: {status}")
            
            return InstitutionalValidationResult(
                approved=approved,
                overall_score=round(overall_score, 2),
                institution_grade=grade,
                validation_status=status,
                warnings=warnings,
                failed_modules=failed,
                recommendations=recs,
                execution_time_ms=round(elapsed, 2)
            )
            
        except Exception as e:
            logger.error(f"Error during institutional validation: {e}")
            elapsed = (datetime.now() - start_time).total_seconds() * 1000.0
            return InstitutionalValidationResult(
                approved=False,
                overall_score=0.0,
                institution_grade=InstitutionGrade.FAILED.value,
                validation_status=ValidationStatus.REJECTED.value,
                warnings=[f"Validation Engine Exception: {e}"],
                failed_modules=["SYSTEM"],
                recommendations=["DO NOT EXECUTE. System error occurred."],
                execution_time_ms=elapsed
            )

    def export_report(self, result: InstitutionalValidationResult, format_type: str = "JSON", output_dir: str = None) -> str:
        out_dir = output_dir or self.export_settings.get("default_export_path", "exports/validation_reports/")
        os.makedirs(out_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        format_type = format_type.upper()
        
        if format_type == "JSON":
            filepath = os.path.join(out_dir, f"validation_{timestamp}.json")
            with open(filepath, "w") as f:
                json.dump(result.to_dict(), f, indent=4)
        elif format_type == "CSV" and self.export_settings.get("enable_csv_export", True):
            filepath = os.path.join(out_dir, f"validation_{timestamp}.csv")
            with open(filepath, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Key", "Value"])
                for k, v in result.to_dict().items():
                    writer.writerow([k, v])
        elif format_type == "PDF" and self.export_settings.get("enable_pdf_export", True):
            filepath = os.path.join(out_dir, f"validation_{timestamp}.pdf")
            with open(filepath, "w") as f:
                f.write("MOCK PDF EXPORT\n")
                f.write(json.dumps(result.to_dict(), indent=2))
        else:
            raise ValueError(f"Format {format_type} not supported or disabled.")
            
        logger.info(f"Validation report exported to {filepath}")
        return filepath
