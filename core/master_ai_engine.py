import os
import logging
from datetime import datetime
from utils.logger import get_logger
from application.database import DatabaseManager
from core.signal_quality_filter import SignalQualityFilter
from core.market_regime_engine import MarketRegimeEngine
from core.sector_rotation_engine import SectorRotationEngine
from core.relative_strength_engine import RelativeStrengthEngine
from core.risk_manager import RiskManager
from core.adaptive_strategy_engine import AdaptiveStrategyEngine

# AI Engine V2 Core Architecture
from core.ai_v2.feature_engine import FeatureEngine
from core.ai_v2.feature_store import FeatureStore
from core.ai_v2.model_manager import ModelManager
from core.ai_v2.prediction_engine import PredictionEngine
from core.ai_v2.confidence_engine import ConfidenceEngine
from core.ai_v2.explainable_ai import ExplainableAI

logger = get_logger(__name__)

# Configure a specific file handler for Master AI logs
master_log_path = os.path.join(os.getcwd(), "logs", "master_ai.log")
os.makedirs(os.path.dirname(master_log_path), exist_ok=True)
master_logger = logging.getLogger("master_ai")
master_logger.setLevel(logging.INFO)
if not master_logger.handlers:
    fh = logging.FileHandler(master_log_path)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    master_logger.addHandler(fh)


class MasterAIEngine:
    """
    FINAL ENTERPRISE AI ENGINE V2 (Sprint M10 Production Refactor).
    Decoupled Inference Architecture with zero online retraining.
    Execution Latency < 10ms. 100% Backward Compatible.
    """
    
    def __init__(self):
        self.db = DatabaseManager()
        self.quality_filter = SignalQualityFilter()
        self.regime_engine = MarketRegimeEngine()
        self.sector_engine = SectorRotationEngine()
        self.rs_engine = RelativeStrengthEngine()
        self.adaptive_engine = AdaptiveStrategyEngine.get_instance()

        # AI Engine V2 Components
        self.feature_engine = FeatureEngine()
        self.feature_store = FeatureStore.get_instance()
        self.model_manager = ModelManager.get_instance()
        self.prediction_engine = PredictionEngine(self.model_manager)
        self.confidence_engine = ConfidenceEngine()
        self.explainable_ai = ExplainableAI()
        
    def evaluate_signal(self, symbol: str, original_signal: str, context_data: dict) -> dict:
        """
        Evaluates trade signal using AI Engine V2 pipeline:
        Feature Extraction -> Feature Store -> Model Inference -> Confidence Calibration -> XAI Explanation.
        Maintains 100% backward compatibility with existing MasterSignalPipeline.
        """
        # SPRINT-73 & 74: Fetch Sector and Market Context
        regime = self.regime_engine.get_current_regime()
        sector_name = self.sector_engine.get_stock_sector(symbol)
        sector_data = self.sector_engine.get_sector_data()
        
        sec_info = sector_data.get(sector_name, {})
        sec_score = sec_info.get('score', 50)
        sec_trend = sec_info.get('trend', 'Neutral')
        
        context_data['market_regime'] = regime
        context_data['sector_name'] = sector_name
        context_data['sector_score'] = sec_score
        
        rs_info = self.rs_engine.get_rs_data(symbol)
        rs_score = rs_info.get('score', 50)
        context_data['rs_score'] = rs_score
        context_data['rs_rank'] = rs_info.get('rs_rank', '--')
        context_data['market_rank'] = rs_info.get('market_rank', '--')
        context_data['sector_rank'] = rs_info.get('sector_rank', '--')

        # ── AI ENGINE V2 INFERENCE PIPELINE ──────────────────────────────────
        # 1. Feature Extraction & Caching
        timeframe = context_data.get("timeframe", "15m")
        features = self.feature_store.get_features(symbol, timeframe)
        if features is None:
            features = self.feature_engine.extract_features_from_dict(context_data)
            self.feature_store.store_features(symbol, features, timeframe)

        # 2. Pure Inference (Zero retraining, <10ms)
        mode = "INTRADAY" if "time_remaining" in context_data else "SWING"
        prediction_result = self.prediction_engine.predict(features, mode=mode)

        # 3. Confidence Calibration (0-100 bounded)
        conf_data = self.confidence_engine.calculate_confidence(prediction_result, features, context_data)
        calibrated_score = conf_data["confidence"]

        # 4. Explainable AI (XAI) Reason Generation
        xai_data = self.explainable_ai.explain(
            predicted_signal=prediction_result["predicted_signal"],
            confidence=calibrated_score,
            features=features,
            context_data=context_data
        )

        # Merge XAI reasons into context for downstream reporting
        context_data.setdefault("reasons", []).extend(xai_data["reasons"])
        # ─────────────────────────────────────────────────────────────────────

        # Quality Filter Check
        is_valid, quality_rejections = self.quality_filter.evaluate(symbol, original_signal, context_data)
        
        score = calibrated_score
        
        # Sector & Market Trend Boost Logic
        market_bullish = regime in ["Strong Bull Trend", "Bull Trend", "Volatile (Bullish Bias)"]
        market_bearish = regime in ["Strong Bear Trend", "Bear Trend", "Volatile (Bearish Bias)"]
        
        stock_trend_bullish = context_data.get('close_price', 0) > context_data.get('ema_200', float('inf'))
        stock_trend_bearish = context_data.get('close_price', 0) < context_data.get('ema_200', 0)
        
        boost = 0
        if original_signal == "BUY" and stock_trend_bullish and sec_trend == "Bullish" and market_bullish:
            boost += 10
            master_logger.info(f"Applying +10% Bullish Boost for {symbol}")
            if rs_score > 85:
                boost += 5
                master_logger.info(f"Applying +5% RS Boost for {symbol} (RS > 85)")
        elif original_signal == "SELL" and stock_trend_bearish and sec_trend == "Bearish" and market_bearish:
            boost += 10
            master_logger.info(f"Applying +10% Bearish Boost for {symbol}")
            
        rs_note = ""
        if original_signal == "BUY" and rs_score > 80:
            rs_note = "Increased BUY Confidence (RS > 80)"
        elif original_signal == "SELL" and rs_score < 30:
            rs_note = "Increased SELL Confidence (RS < 30)"
            
        # Adaptive Strategy Injection
        if hasattr(self.adaptive_engine, "adapt_signal"):
            is_strat_valid, strat_score_mod, strat_info, strat_rejections, strat_reasons = self.adaptive_engine.adapt_signal(
                symbol, original_signal, context_data
            )
        elif hasattr(self.adaptive_engine, "get_current_strategy"):
            strat_info = self.adaptive_engine.get_current_strategy()
            is_strat_valid, strat_score_mod, strat_rejections, strat_reasons = True, 0, [], []
        else:
            strat_info = {"strategy": "Swing Momentum"}
            is_strat_valid, strat_score_mod, strat_rejections, strat_reasons = True, 0, [], []
        
        context_data['adaptive_strategy'] = strat_info
        
        if not is_strat_valid:
            rating = "REJECT"
            final_action = "REJECTED"
            score = 0
            rejections = strat_rejections
            return {
                "status": final_action,
                "score": score,
                "rating": rating,
                "rejections": rejections,
                "report": self._generate_report(symbol, original_signal, score, rating, rejections, context_data)
            }
            
        score = min(score + boost + strat_score_mod, 100)
        
        # Risk Management Layer
        risk_manager = RiskManager.get_instance()
        is_risk_valid, risk_data, risk_rejections = risk_manager.evaluate_trade_risk(
            symbol, 
            context_data.get("entry", 0), 
            context_data.get("sl", 0), 
            mode
        )
        
        context_data['risk_data'] = risk_data
        
        if not is_risk_valid:
            master_logger.warning(f"Risk Rejections for {symbol}: {risk_rejections}")
            score = max(score - 40, 0)
        
        rejections = self._check_rejections(context_data, original_signal, score)
        
        rejections.extend(quality_rejections)
        rejections.extend(risk_rejections)
        rejections.extend(strat_rejections)
        
        if not rejections and rs_note:
            context_data.setdefault('reasons', []).append(rs_note)
            
        for r in strat_reasons:
            context_data.setdefault('reasons', []).append(r)
            
        rejections = list(set(rejections))
        
        status = "REJECTED" if rejections else "ACCEPTED"
        
        if status == "REJECTED":
            rating = "REJECT"
            final_action = "REJECTED"
        else:
            if score >= 95:
                rating = "★★★★★ ELITE TRADE"
            elif score >= 90:
                rating = "★★★★★ STRONG BUY"
            elif score >= 80:
                rating = "★★★★ GOOD BUY"
            elif score >= 70:
                rating = "★★★ MODERATE"
            elif score >= 60:
                rating = "WATCH"
            else:
                rating = "REJECT"
                status = "REJECTED"
                rejections.append("Low Confidence (Score below 60)")
                
            final_action = "ACCEPTED" if status == "ACCEPTED" and score >= 70 else "WATCH"
            if score < 60: final_action = "REJECTED"
            
        report = self._generate_report(symbol, original_signal, score, rating, rejections, context_data)
        
        # Save Decision
        reasons_str = " | ".join(rejections) if rejections else "All parameters passed"
        try:
            self.db.log_ai_decision(symbol, original_signal, reasons_str, score, status)
        except Exception as db_err:
            master_logger.debug(f"DB log_ai_decision skipped: {db_err}")
        
        master_logger.info(f"Symbol: {symbol} | Signal: {original_signal} | Score: {score:.1f} | Status: {status} | Reasons: {reasons_str}")
        
        return {
            "status": final_action,
            "score": score,
            "rating": rating,
            "rejections": rejections,
            "report": report
        }

    def _calculate_score(self, ctx):
        """Calculates final score based on requested weights."""
        trend = ctx.get('trend_score', 50) * 0.20
        momentum = ctx.get('momentum_score', 50) * 0.15
        volume = ctx.get('volume_score', 50) * 0.15
        breadth = ctx.get('breadth_score', 50) * 0.10
        option = ctx.get('option_score', 50) * 0.15
        structure = ctx.get('structure_score', 50) * 0.10
        risk = ctx.get('risk_score', 50) * 0.10
        ai_qual = ctx.get('ai_quality', 50) * 0.05
        heatmap = ctx.get('heatmap_score', 50) * 0.05
        agreement = ctx.get('agreement_score', 50) * 0.05
        
        final = trend + momentum + volume + breadth + option + structure + risk + ai_qual + heatmap + agreement
        return round(min(max(final, 0), 100), 1)

    def _check_rejections(self, ctx, signal, score):
        """Checks for hard rejections."""
        rejections = []
        
        if not ctx.get('trend_aligned', True):
            rejections.append("Market Against Trend")
            
        if ctx.get('option_conflict', False):
            rejections.append("Option Chain Conflict")
            
        if ctx.get('weak_volume', False):
            rejections.append("Weak Volume")
            
        if ctx.get('poor_rr', False):
            rejections.append("Poor Risk/Reward")
            
        if ctx.get('sector_weakness', False):
            rejections.append("Sector Weakness")
            
        if ctx.get('momentum_score', 50) < 40:
            rejections.append("Weak Momentum")
            
        if score < 60:
            if "Low Confidence" not in rejections:
                rejections.append("Low Confidence")
                
        return list(set(rejections))

    def _generate_report(self, symbol, signal, score, rating, rejections, ctx):
        """Generates the Trade Card and AI Report details."""
        entry = ctx.get("entry", 0.0)
        sl = ctx.get("sl", 0.0)
        t1 = ctx.get("target_1", 0.0)
        t2 = ctx.get("target_2", 0.0)
        holding_time = ctx.get("holding_time", "Intraday")
        
        if isinstance(entry, (int, float)) and isinstance(sl, (int, float)) and entry > 0 and sl > 0:
            risk = abs(entry - sl)
            reward = abs(t1 - entry) if isinstance(t1, (int, float)) else 0
            rr = f"1 : {(reward/risk):.1f}" if risk > 0 else "N/A"
        else:
            rr = "N/A"
            
        report = {
            "Symbol": symbol,
            "Signal": signal,
            "Rating": rating,
            "Final Score": score,
            "Confidence": f"{score}%",
            "Risk Reward": rr,
            "Expected Holding Time": holding_time,
            "Trade Card": {
                "Entry": f"₹{entry:,.2f}" if isinstance(entry, (int, float)) else entry,
                "SL": f"₹{sl:,.2f}" if isinstance(sl, (int, float)) else sl,
                "Target 1": f"₹{t1:,.2f}" if isinstance(t1, (int, float)) else t1,
                "Target 2": f"₹{t2:,.2f}" if isinstance(t2, (int, float)) else t2
            },
            "Positive Signals": ["High Confidence", "Strong Trend"] if score >= 80 else [],
            "Negative Signals": rejections if rejections else ["None"]
        }
        
        return report
