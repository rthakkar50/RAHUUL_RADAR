import logging
import time
from typing import Any, Dict, Tuple, List, Optional

logger = logging.getLogger("MasterSignalPipeline")

# Module Constants for Pipeline Configuration & Graceful Fallbacks
DEFAULT_CONFIDENCE_REDUCTION_PCT = 10.0
DEFAULT_MTF_CONFIRMED_SCORE = 100.0
DEFAULT_MTF_DEGRADED_SCORE = 50.0
DEFAULT_RISK_REWARD_RATIO = 2.0
DEFAULT_PRICE = 100.0
DEFAULT_QUANTITY = 10
DEFAULT_SCORE = 50.0
HIGH_SCORE_THRESHOLD = 80.0
LOW_SCORE_THRESHOLD = 20.0
DEFAULT_TIMEFRAME = "15m"


class MasterSignalPipeline:
    """
    Orchestrates the entire trade signal validation pipeline.
    
    FLOW:
    Market Data -> Trend Engine -> Momentum Engine -> Volume Engine -> Structure Engine -> 
    Relative Strength -> Sector Rotation -> Adaptive Strategy -> Risk Manager -> Master AI -> Approved Signal
    """
    
    def __init__(self, engines=None):
        """
        engines: dictionary of instantiated engine objects.
        Expected keys: 'trend', 'momentum', 'volume', 'structure', 'risk', 
        'relative_strength', 'sector_rotation', 'adaptive_strategy', 'master_ai'
        """
        self.engines = engines or {}
        self.rejection_reasons = []
        self.false_signal_report = None
        self.explanation = None

    def run(self, *args, decision: str = "WATCH", confidence: float = 0.0, **kwargs):
        """
        Executes the master pipeline on incoming market data.
        Refactored into private stage methods for production audit compliance.
        """
        pipeline_start = time.time()
        symbol = kwargs.get("symbol", "UNKNOWN")
        logger.info(f"Pipeline Request: symbol={symbol}, decision={decision}, confidence={confidence}")
        
        # 1. Validation & Input Mapping
        collected_results, weighted_score, mapped_input, pipeline_status = self._run_validation(
            *args, decision=decision, confidence=confidence, **kwargs
        )

        # 2. False Signal Detection
        false_signal_res = self._run_false_signal(mapped_input, decision, confidence, weighted_score)
        if false_signal_res is not None:
            return false_signal_res

        # 3. Multi-Timeframe Alignment
        mtf_res = self._run_mtf(kwargs, mapped_input, confidence, weighted_score)
        if mtf_res.get("status") == "REJECTED":
            return {
                "status": "REJECTED",
                "score": weighted_score,
                "report": mtf_res.get("report")
            }
        
        alignment_status = mtf_res["alignment_status"]
        alignment_score = mtf_res["alignment_score"]
        alignment_report = mtf_res["alignment_report"]
        confidence = mtf_res["confidence"]

        # 4. Smart Entry & Risk-Reward Optimization
        entry_data = self._run_entry(
            collected_results, kwargs, decision, weighted_score, confidence, alignment_score, alignment_report, mapped_input
        )
        weighted_score = entry_data["weighted_score"]
        confidence = entry_data["confidence"]
        decision = entry_data["decision"]
        entry_score = entry_data["entry_score"]
        rec_entry = entry_data["rec_entry"]
        sl_level = entry_data["sl_level"]
        t1, t2, t3 = entry_data["t1"], entry_data["t2"], entry_data["t3"]
        rr_ratio = entry_data["rr_ratio"]
        srre_result = entry_data.get("srre_result")

        # 5. Position Exit Evaluation
        exit_data = self._run_exit(kwargs, decision)

        # 6. Final Summary & Calibration
        return self._run_summary(
            collected_results=collected_results,
            pipeline_status=pipeline_status,
            mapped_input=mapped_input,
            alignment_status=alignment_status,
            alignment_score=alignment_score,
            alignment_report=alignment_report,
            entry_score=entry_score,
            rec_entry=rec_entry,
            sl_level=sl_level,
            t1=t1, t2=t2, t3=t3,
            rr_ratio=rr_ratio,
            exit_data=exit_data,
            srre_result=srre_result,
            weighted_score=weighted_score,
            confidence=confidence,
            decision=decision,
            symbol=symbol,
            pipeline_start=pipeline_start,
            kwargs=kwargs
        )

    def _run_validation(self, *args, decision: str = "WATCH", confidence: float = 0.0, symbol: str = "UNKNOWN", **kwargs):
        """Private helper: Collects engine results, validates completeness, calculates weighted score, and maps inputs."""
        mapping_start = time.time()
        collected_results = self.collect_results(*args, **kwargs)
        valid, missing = self.validate(collected_results)
        pipeline_status = "SUCCESS" if valid else f"INCOMPLETE: Missing {missing}"
        
        from core.decision_weight_engine import DecisionWeightEngine
        weight_engine = DecisionWeightEngine()
        weighted_score = weight_engine.calculate_weighted_score(collected_results)
        
        mapped_input = {
            "Trend": collected_results.get("trend"),
            "Momentum": collected_results.get("momentum"),
            "Volume": collected_results.get("volume"),
            "Structure": collected_results.get("structure"),
            "Risk": collected_results.get("risk"),
            "Relative Strength": collected_results.get("relative_strength"),
            "Sector Rotation": collected_results.get("sector_rotation"),
            "Option Chain": collected_results.get("option_chain"),
            "Market Regime": collected_results.get("market_regime"),
            "Adaptive Strategy": collected_results.get("adaptive_strategy"),
            "Master AI": collected_results.get("master_ai"),
            "Weighted Score": weighted_score,
            "decision": decision,
            "confidence": confidence
        }
        mapping_time = time.time() - mapping_start
        logger.info(f"Pipeline Mapping Complete: symbol={symbol}, Mapping Time={mapping_time:.4f}s")
        return collected_results, weighted_score, mapped_input, pipeline_status

    def _run_false_signal(self, mapped_input: dict, decision: str, confidence: float, weighted_score: float) -> Optional[dict]:
        """Private helper: Runs FalseSignalDetector and returns rejection response if triggered."""
        from core.false_signal_detector import FalseSignalDetector
        from core.false_signal_report import FalseSignalReport
        
        detector = FalseSignalDetector()
        is_rejected = False
        reasons = []
        
        try:
            detection_result = detector.detect(mapped_input, decision)
            if detection_result.get("status") == "REJECTED":
                is_rejected = True
                reasons = detection_result.get("reasons", [])
        except Exception:
            logger.exception("FalseSignalDetector failed. Continuing pipeline using previous behavior.")
            is_rejected = False
            reasons = []

        if is_rejected:
            report = FalseSignalReport(
                status="REJECTED",
                reasons=reasons,
                confidence=confidence,
                score=weighted_score
            )
            self.rejection_reasons = reasons
            self.false_signal_report = report
            return {
                "status": "REJECTED",
                "score": weighted_score,
                "report": report
            }
            
        self.rejection_reasons = []
        self.false_signal_report = None
        return None

    def _run_mtf(self, kwargs: dict, mapped_input: dict, confidence: float, weighted_score: float) -> dict:
        """Private helper: Runs MultiTimeframeEngine alignment logic and adjusts confidence."""
        mtf_data = kwargs.get("mtf_data")
        logger.debug(f"Pipeline kwargs keys: {kwargs.keys()}")
        logger.debug(f"Pipeline mtf_data value: {mtf_data} | type: {type(mtf_data)}")
        
        alignment_status = "CONFIRMED"
        alignment_score = DEFAULT_MTF_CONFIRMED_SCORE
        alignment_report = None
        
        if mtf_data is not None:
            real_status = getattr(mtf_data, "alignment_status", "No Alignment")
            
            if "Perfect Alignment" in real_status:
                alignment_status = "CONFIRMED"
            elif "Major Conflict" in real_status or "No Alignment" in real_status:
                alignment_status = "REJECTED"
            else:
                alignment_status = "PARTIAL"
                
            alignment_score = float(getattr(mtf_data, "confluence_score", 0.0))
            alignment_report = getattr(mtf_data, "reasons", ["Real MTF Alignment Used"])
        else:
            logger.warning("mtf_data was missing or None in MasterSignalPipeline. Applying graceful degradation.")
            alignment_status = "CONFIRMED"
            alignment_score = DEFAULT_MTF_DEGRADED_SCORE
            alignment_report = ["Warning: Missing MTF Data"]

        if alignment_status == "REJECTED":
            self.false_signal_report = alignment_report
            return {
                "status": "REJECTED",
                "alignment_status": alignment_status,
                "alignment_score": alignment_score,
                "alignment_report": alignment_report,
                "confidence": confidence,
                "report": alignment_report
            }
            
        elif alignment_status == "PARTIAL":
            reduction_pct = kwargs.get("confidence_reduction_pct", DEFAULT_CONFIDENCE_REDUCTION_PCT)
            confidence = confidence * (1.0 - reduction_pct / 100.0)
            mapped_input["confidence"] = confidence

        return {
            "status": "CONTINUE",
            "alignment_status": alignment_status,
            "alignment_score": alignment_score,
            "alignment_report": alignment_report,
            "confidence": confidence
        }

    def _run_entry(self, collected_results: dict, kwargs: dict, decision: str, weighted_score: float,
                   confidence: float, alignment_score: float, alignment_report: list, mapped_input: dict) -> dict:
        """Private helper: Evaluates smart entry optimization and risk-reward calculation."""
        from core.smart_entry_optimizer import SmartEntryOptimizer, EntryCandidate
        from core.risk_reward_engine import RiskRewardEngine
        
        optimizer = SmartEntryOptimizer()
        srre = RiskRewardEngine()
        entry_score = 0.0
        rec_entry = 0.0
        sl_level = 0.0
        t1, t2, t3 = 0.0, 0.0, 0.0
        rr_ratio = kwargs.get("risk_reward", DEFAULT_RISK_REWARD_RATIO)
        srre_result = None
        
        try:
            optimizer.evaluate_entry()
            
            def to_float(val, default=DEFAULT_SCORE):
                if isinstance(val, dict):
                    val = val.get("score", default)
                if isinstance(val, (int, float)):
                    return float(val)
                if isinstance(val, str):
                    val_upper = val.upper()
                    if val_upper in ("BULL", "BULLISH", "STRONG", "HIGH", "LEADING"):
                        return HIGH_SCORE_THRESHOLD
                    if val_upper in ("BEAR", "BEARISH", "WEAK", "LOW", "LAGGING"):
                        return LOW_SCORE_THRESHOLD
                    try:
                        return float(val)
                    except ValueError:
                        pass
                return default
            
            rel_strength = to_float(collected_results.get("relative_strength"))
            trend_power = to_float(collected_results.get("trend"))
            vol_confirm = to_float(collected_results.get("volume"))
            
            candidate = EntryCandidate(
                symbol=kwargs.get("symbol", "UNKNOWN"),
                price=float(kwargs.get("price", DEFAULT_PRICE)),
                signal_direction=decision,
                signal_strength=weighted_score,
                timeframe=kwargs.get("timeframe", DEFAULT_TIMEFRAME)
            )
            
            entry_score = optimizer.calculate_entry_score(
                candidate,
                relative_strength=rel_strength,
                trend_strength=trend_power,
                volume_confirmation=vol_confirm,
                mtf_alignment=alignment_score
            )
            
            rec_entry = optimizer.recommend_entry(candidate, entry_score)
            
            atr_val = float(kwargs.get("atr", 0.0))
            struct_dict = kwargs.get("structure", {})
            structure_details = struct_dict.get("details", {}) if isinstance(struct_dict, dict) else {}
            
            sl_level = optimizer.recommend_stop_loss(candidate, rec_entry, rr_ratio, atr=atr_val, structure_details=structure_details)
            t1, t2, t3 = optimizer.recommend_targets(candidate, rec_entry, sl_level, structure_details=structure_details)
            
            srre_result = srre.evaluate(
                entry_price=rec_entry,
                stop_loss=sl_level,
                target_1=t1,
                target_2=t2,
                atr=atr_val,
                trade_direction=decision
            )
            
            rr_ratio = srre_result.rr_ratio
            for r in srre_result.reasons:
                alignment_report.append(r)
                
            if srre_result.recommendation == "REJECT":
                weighted_score = 0.0
                confidence = 0.0
                decision = "WAIT"
                alignment_report.append("⛔ TRADE REJECTED BY SMART RISK REWARD ENGINE (POOR R/R).")
                mapped_input["confidence"] = confidence
            
        except Exception:
            logger.exception("SmartEntryOptimizer/SRRE failed. Continuing pipeline using previous behavior.")
            entry_score = 0.0
            rec_entry = float(kwargs.get("price", DEFAULT_PRICE))
            sl_level = 0.0
            t1, t2, t3 = 0.0, 0.0, 0.0
            rr_ratio = 0.0
            srre_result = None

        return {
            "weighted_score": weighted_score,
            "confidence": confidence,
            "decision": decision,
            "entry_score": entry_score,
            "rec_entry": rec_entry,
            "sl_level": sl_level,
            "t1": t1, "t2": t2, "t3": t3,
            "rr_ratio": rr_ratio,
            "srre_result": srre_result
        }

    def _run_exit(self, kwargs: dict, decision: str) -> dict:
        """Private helper: Evaluates open position exit conditions using AIExitManager."""
        from core.ai_exit_manager import AIExitManager, OpenPosition
        from datetime import datetime
        
        exit_manager = AIExitManager()
        try:
            pos_data = kwargs.get("position")
            if isinstance(pos_data, OpenPosition):
                position = pos_data
            elif isinstance(pos_data, dict):
                position = OpenPosition.from_dict(pos_data)
            else:
                position = OpenPosition(
                    symbol=kwargs.get("symbol", "UNKNOWN"),
                    direction=decision,
                    entry_price=float(kwargs.get("price", DEFAULT_PRICE)),
                    current_price=float(kwargs.get("price", DEFAULT_PRICE)),
                    quantity=int(kwargs.get("quantity", DEFAULT_QUANTITY)),
                    entry_time=datetime.now(),
                    current_pnl=float(kwargs.get("current_pnl", 0.0)),
                    holding_minutes=int(kwargs.get("holding_minutes", 0))
                )
            
            exit_decision = exit_manager.evaluate_position(position)
            rec_action = exit_manager.recommend_exit(position, exit_decision)
            rec_ts = exit_manager.recommend_trailing_stop(position, exit_decision)
            rec_pe = exit_manager.recommend_partial_exit(position, exit_decision)
            
            return {
                "exit_action": rec_action,
                "exit_reason": exit_decision.reason,
                "trailing_stop": rec_ts,
                "partial_exit_percentage": rec_pe,
                "exit_confidence": exit_decision.confidence
            }
        except Exception as e:
            logger.exception("AIExitManager failed. Continuing pipeline using previous behavior.")
            return {
                "exit_action": "HOLD",
                "exit_reason": f"Exit Evaluation Error: {e}",
                "trailing_stop": 0.0,
                "partial_exit_percentage": 0.0,
                "exit_confidence": 0.0
            }

    def _run_summary(self, collected_results: dict, pipeline_status: str, mapped_input: dict,
                     alignment_status: str, alignment_score: float, alignment_report: list,
                     entry_score: float, rec_entry: float, sl_level: float, t1: float, t2: float, t3: float,
                     rr_ratio: float, exit_data: dict, srre_result: Any, weighted_score: float,
                     confidence: float, decision: str, symbol: str, pipeline_start: float, kwargs: dict) -> dict:
        """Private helper: Builds signal explanation, confidence calibration, TERE readiness, and final output summary."""
        from core.signal_explainer import SignalExplainer
        explainer = SignalExplainer()
        self.explanation = explainer.build_explanation(mapped_input)
        
        from core.confidence_calibration_engine import ConfidenceCalibrationEngine, ConfidenceInput
        conf_engine = ConfidenceCalibrationEngine()
        
        def extract_score(res, d=50.0):
            if res is None: return d
            if hasattr(res, "score"):
                try: return float(res.score)
                except: return d
            if isinstance(res, dict) and "score" in res:
                try: return float(res["score"])
                except: return d
            return d
            
        def extract_str(res, key, d="Neutral"):
            if res is None: return d
            if hasattr(res, key): return getattr(res, key)
            if isinstance(res, dict) and key in res: return res[key]
            return d
            
        conf_input = ConfidenceInput(
            symbol=kwargs.get("symbol", "UNKNOWN"),
            price=float(kwargs.get("price", 0.0)),
            signal_direction=decision,
            trend_score=extract_score(collected_results.get("trend")),
            momentum_score=extract_score(collected_results.get("momentum")),
            volume_score=extract_score(collected_results.get("volume")),
            relative_strength_score=extract_score(collected_results.get("relative_strength")),
            sector_rotation_score=extract_score(collected_results.get("sector_rotation")),
            structure_score=extract_score(collected_results.get("structure")),
            structure_quality=extract_str(collected_results.get("structure"), "current_structure", "Neutral"),
            mtf_score=alignment_score,
            mtf_status=alignment_status,
            adx_value=extract_score(collected_results.get("adx"), 0.0),
            avwap_status=extract_str(collected_results.get("avwap"), "position", "Neutral"),
            risk_reward_ratio=rr_ratio,
            risk_reward_score=srre_result.risk_score if srre_result is not None and hasattr(srre_result, "risk_score") else 50.0,
            market_regime=extract_str(collected_results.get("market"), "market_bias", "Neutral")
        )
        conf_res = conf_engine.calibrate_confidence(conf_input)
        conf_payload = {
            "confidence": conf_res.confidence,
            "grade": conf_res.grade,
            "reasons": conf_res.reasons,
            "positive_factors": conf_res.positive_factors,
            "negative_factors": conf_res.negative_factors
        }
        
        from core.trade_execution_readiness_engine import TradeExecutionReadinessEngine, ExecutionInput
        tere = TradeExecutionReadinessEngine()
        tere_input = ExecutionInput(
            elite_score=weighted_score,
            confidence=conf_res.confidence,
            structure_score=extract_score(collected_results.get("structure")),
            adx_value=extract_score(collected_results.get("adx"), 0.0),
            volume_score=extract_score(collected_results.get("volume")),
            risk_reward_score=srre_result.risk_score if srre_result is not None and hasattr(srre_result, "risk_score") else 50.0,
            market_regime=extract_str(collected_results.get("market"), "market_bias", "Neutral"),
            breakout_status=extract_str(collected_results.get("structure"), "current_structure", "Confirmed")
        )
        tere_res = tere.evaluate_readiness(tere_input)

        existing_pipeline_result = self.generate_summary(
            collected_results, 
            pipeline_status,
            alignment_status=alignment_status,
            alignment_score=alignment_score,
            alignment_report=alignment_report,
            entry_score=entry_score,
            recommended_entry=rec_entry,
            stop_loss=sl_level,
            target_1=t1,
            target_2=t2,
            target_3=t3,
            risk_reward=rr_ratio,
            exit_action=exit_data["exit_action"],
            exit_reason=exit_data["exit_reason"],
            trailing_stop=exit_data["trailing_stop"],
            partial_exit_percentage=exit_data["partial_exit_percentage"],
            exit_confidence=exit_data["exit_confidence"],
            confidence_result=conf_payload
        )
        exec_time = time.time() - pipeline_start
        calibrated_conf = conf_res.confidence if hasattr(conf_res, 'confidence') else confidence
        
        logger.info(
            f"Pipeline Success: symbol={symbol}, Score={weighted_score}, "
            f"Calibrated Confidence={calibrated_conf}%, Execution Time={exec_time:.4f}s"
        )
        
        return {
            "status": "APPROVED",
            "score": weighted_score,
            "entry_score": entry_score,
            "recommended_entry": rec_entry,
            "stop_loss": sl_level,
            "target_1": t1,
            "target_2": t2,
            "target_3": t3,
            "risk_reward": rr_ratio,
            "exit_action": exit_data["exit_action"],
            "exit_reason": exit_data["exit_reason"],
            "trailing_stop": exit_data["trailing_stop"],
            "partial_exit_percentage": exit_data["partial_exit_percentage"],
            "exit_confidence": exit_data["exit_confidence"],
            "calibrated_confidence": calibrated_conf,
            "execution_status": tere_res.status,
            "execution_score": tere_res.score,
            "execution_reason": tere_res.reason,
            "data": existing_pipeline_result
        }
        
    def validate(self, collected_results: dict):
        """
        Validates that all required engine outputs exist.

        Args:
            collected_results: A dictionary containing engine outputs.

        Returns:
            Tuple[bool, list]: (True, []) if all required keys exist and are not None,
                               (False, missing_keys) otherwise.
        """
        required_keys = [
            "trend", "momentum", "volume", "structure", "risk",
            "relative_strength", "sector_rotation", "adaptive_strategy", "master_ai"
        ]
        
        if not isinstance(collected_results, dict):
            return False, required_keys

        missing_keys = [key for key in required_keys if key not in collected_results or collected_results[key] is None]
        
        if missing_keys:
            return False, missing_keys
        return True, []
        
    def collect_results(self, *args, **kwargs):
        """
        Gathers the evaluation results from all engines.
        """
        results = {
            "trend": None,
            "momentum": None,
            "volume": None,
            "structure": None,
            "risk": None,
            "relative_strength": None,
            "sector_rotation": None,
            "adaptive_strategy": None,
            "master_ai": None,
            "adx": None,
            "avwap": None
        }
        
        for key in results.keys():
            # SPRINT-77 FIX: Do not recalculate if the caller explicitly provided the value
            if key in kwargs and kwargs[key] is not None:
                results[key] = kwargs[key]
                continue
                
            if key in self.engines and self.engines[key]:
                try:
                    engine_instance = self.engines[key]
                    
                    # Dynamically call the known public interface of the engine
                    if hasattr(engine_instance, 'evaluate_snapshot'):
                        results[key] = engine_instance.evaluate_snapshot(*args, **kwargs)
                    elif hasattr(engine_instance, 'evaluate_signal'):
                        results[key] = engine_instance.evaluate_signal(*args, **kwargs)
                    elif hasattr(engine_instance, 'evaluate_trade_risk'):
                        results[key] = engine_instance.evaluate_trade_risk(*args, **kwargs)
                    elif hasattr(engine_instance, 'evaluate'):
                        results[key] = engine_instance.evaluate(*args, **kwargs)
                    elif hasattr(engine_instance, 'calculate'):
                        results[key] = engine_instance.calculate(*args, **kwargs)
                    elif callable(engine_instance):
                        results[key] = engine_instance(*args, **kwargs)
                    else:
                        results[key] = "NO_PUBLIC_INTERFACE"
                        
                except Exception as e:
                    logger.exception(f"Engine '{key}' failed during collection")
                    results[key] = kwargs.get(key, None)
            else:
                results[key] = kwargs.get(key, None)
                    
        return results
        
    def generate_summary(self, collected_results: dict, pipeline_status: str,
                         alignment_status: str = None, alignment_score: float = None,
                         alignment_report: Any = None, entry_score: float = None,
                         recommended_entry: float = None, stop_loss: float = None,
                         target_1: float = None, target_2: float = None,
                         target_3: float = None, risk_reward: float = None,
                         exit_action: str = None, exit_reason: str = None,
                         trailing_stop: float = None, partial_exit_percentage: float = None,
                         exit_confidence: float = None,
                         confidence_result: dict = None,
                         performance_result: dict = None) -> dict:
        """
        Generates the final decision summary for the signal.

        Args:
            collected_results: A dictionary containing engine outputs.
            pipeline_status: The execution status of the pipeline.
            alignment_status: Multi-timeframe alignment status.
            alignment_score: Multi-timeframe alignment score.
            alignment_report: Multi-timeframe alignment report.
            entry_score: Optimized entry score rating.
            recommended_entry: Ideal recommended entry price level.
            stop_loss: Recommended defensive stop loss price level.
            target_1: Recommended primary take profit.
            target_2: Recommended secondary take profit.
            target_3: Recommended tertiary take profit.
            risk_reward: Proposed risk-to-reward target ratio.
            exit_action: Decision path action for the position ('HOLD', 'EXIT', etc).
            exit_reason: Structural reason for the exit decision path.
            trailing_stop: Trailing stop level proposed.
            partial_exit_percentage: Percentage size of partial position close.
            exit_confidence: Confidence level (0-100) behind the exit assessment.

        Returns:
            dict: The mapped summary of all indicators and status.
        """
        if not isinstance(collected_results, dict):
            collected_results = {}

        return {
            "Market Trend": collected_results.get("trend"),
            "Momentum": collected_results.get("momentum"),
            "Volume": collected_results.get("volume"),
            "Structure": collected_results.get("structure"),
            "Risk": collected_results.get("risk"),
            "Relative Strength": collected_results.get("relative_strength"),
            "Sector Rotation": collected_results.get("sector_rotation"),
            "Adaptive Strategy": collected_results.get("adaptive_strategy"),
            "Master AI": collected_results.get("master_ai"),
            "Pipeline Status": pipeline_status,
            "alignment_status": alignment_status,
            "alignment_score": alignment_score,
            "alignment_report": alignment_report,
            "entry_score": entry_score,
            "recommended_entry": recommended_entry,
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "target_3": target_3,
            "risk_reward": risk_reward,
            "exit_action": exit_action,
            "exit_reason": exit_reason,
            "trailing_stop": trailing_stop,
            "partial_exit_percentage": partial_exit_percentage,
            "exit_confidence": exit_confidence,
            "confidence_calibration": confidence_result,
            "performance_optimization": performance_result
        }

    def run_strategy_validation(self, strategy_name: str, trades: list) -> dict:
        from core.walk_forward_validator import WalkForwardValidator
        validator = WalkForwardValidator()
        metrics = validator.run_validation(strategy_name, trades)
        report = validator.generate_validation_report(metrics)
        return report

    def run_strategy_ranking(self, strategies_metrics: list) -> dict:
        from core.strategy_ranking_engine import StrategyRankingEngine
        ranker = StrategyRankingEngine()
        ranks = ranker.rank_strategies(strategies_metrics)
        report = ranker.generate_ranking_report(ranks)
        return report
        
    def evaluate_system_performance(self, metrics_data: dict) -> dict:
        from core.performance_optimizer import PerformanceOptimizer, PerformanceMetrics
        optimizer = PerformanceOptimizer()
        try:
            metrics_obj = PerformanceMetrics.from_dict(metrics_data)
        except Exception:
            metrics_obj = PerformanceMetrics(0.0, 0.0, 0.0, 0.0, 0, 0, 0.0)
        result = optimizer.collect_metrics(metrics_obj)
        return optimizer.generate_report(result)
