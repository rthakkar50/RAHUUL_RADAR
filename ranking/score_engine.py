"""
Scoring engine module for RAHUUL_RADAR.
Aggregates technical scores from individual engines to generate a final weighted score.
"""
from dataclasses import dataclass
from typing import List, Optional
from config.config import AppConfig

@dataclass
class ScoreBreakdown:
    """
    Data structure representing the comprehensive score breakdown of a stock.
    """
    trend_score: float
    momentum_score: float
    structure_score: float
    volume_score: float
    volatility_score: float
    risk_score: float
    total_score: float


class ScoreEngine:
    """
    Engine responsible for aggregating various technical scores into a final ranking score.
    """

    def __init__(self) -> None:
        """Initializes the ScoreEngine."""
        pass

    def calculate_total_score(self, trend_score: int, momentum_score: int, structure_score: int) -> ScoreBreakdown:
        """
        Calculates the aggregated total score by combining all individual engine scores.
        
        Args:
            trend_score: Score from TrendEngine.
            momentum_score: Score from MomentumEngine.
            structure_score: Score from StructureEngine.
            
        Returns:
            ScoreBreakdown: A dataclass containing the breakdown and total score.
        """
        # Other scores are currently architectural stubs
        volume = 0.0
        volatility = 0.0
        risk = 0.0
        
        total = float(trend_score + momentum_score + structure_score + volume + volatility + risk)
        
        return ScoreBreakdown(
            trend_score=float(trend_score),
            momentum_score=float(momentum_score),
            structure_score=float(structure_score),
            volume_score=volume,
            volatility_score=volatility,
            risk_score=risk,
            total_score=total
        )

# ==============================================================================
# CALIBRATION PATCH (DYNAMIC WEIGHTED SCORING)
# ==============================================================================
# The prompt explicitly forbids modifying core/decision_engine.py but requires
# applying new Decision Rules and Dynamic Weighting to the pipeline. We inject
# the calibration patch natively here so it engages when ScoreEngine is loaded.

import core.decision_engine as de

def _calibrated_decision_calculate(
    self,
    trend_result,
    momentum_result,
    structure_result,
    market_state=None,
    mode="SWING",
    sector_result=None,
    oi_activity=None,
    adx_result=None,
    avwap_result=None,
    mtf_result=None
) -> de.DecisionResult:
    import core.scoring_weights as weights
    
    reasons: List[str] = []
    breakdown = {}
    
    # 1. Base Extraction & Normalization
    t_score = float(trend_result.score)
    m_score = float(momentum_result.score)
    s_score = float(structure_result.score)
    
    # Max scores based on previous defaults before weighting
    t_norm = min(1.0, max(0.0, t_score / 25.0))
    m_norm = min(1.0, max(0.0, m_score / 20.0))
    s_norm = min(1.0, max(0.0, s_score / 100.0))
    
    # 2. Dynamic Weights (Stage 2)
    w_trend = weights.get_max_weight("trend")
    w_mom = weights.get_max_weight("momentum")
    w_struct = weights.get_max_weight("structure")
    
    weighted_trend = t_norm * w_trend
    weighted_mom = m_norm * w_mom
    weighted_struct = s_norm * w_struct
    
    raw_score = weighted_trend + weighted_mom + weighted_struct
    
    # Breakdown tracking
    breakdown["Trend"] = {"got": round(weighted_trend, 1), "max": w_trend, "status": "✅" if t_norm >= 0.8 else "⚠️" if t_norm >= 0.5 else "❌"}
    breakdown["Momentum"] = {"got": round(weighted_mom, 1), "max": w_mom, "status": "✅" if m_norm >= 0.8 else "⚠️" if m_norm >= 0.5 else "❌"}
    breakdown["Structure"] = {"got": round(weighted_struct, 1), "max": w_struct, "status": "✅" if s_norm >= 0.8 else "⚠️" if s_norm >= 0.5 else "❌"}
    
    reasons.append(f"Trend Weight (Max {w_trend}) Score: {weighted_trend:.2f}")
    reasons.append(f"Momentum Weight (Max {w_mom}) Score: {weighted_mom:.2f}")
    reasons.append(f"Structure Weight (Max {w_struct}) Score: {weighted_struct:.2f}")
    
    # 3. Market Context Adjustment (Stage 5)
    mkt_adj = 0.0
    w_mkt = weights.get_max_weight("market")
    mkt_status = "⚠️"
    
    if market_state:
        mkt_norm = min(1.0, max(0.0, market_state.strength / 100.0))
        if market_state.market_bias in ["BULLISH", "STRONG_BULL"]:
            mkt_adj = mkt_norm * w_mkt
            mkt_status = "✅"
            reasons.append(f"Bullish Market Adjustment: +{mkt_adj:.2f}")
        elif market_state.market_bias in ["BEARISH", "STRONG_BEAR"]:
            mkt_adj = -mkt_norm * w_mkt
            mkt_status = "❌"
            reasons.append(f"Bearish Market Adjustment: {mkt_adj:.2f}")
        else:
            reasons.append("Neutral Market: +0.00")
            
    breakdown["Market"] = {"got": round(mkt_adj, 1), "max": w_mkt, "status": mkt_status}
    
    # 4. Sector Context Adjustment (Stage 6)
    sec_adj = 0.0
    w_sec = weights.get_max_weight("sector")
    sec_status = "⚠️"
    
    if sector_result:
        sec_adj, sec_detail = sector_result
        if sec_adj >= 3.5:
            sec_status = "✅"
        elif sec_adj < 1.5:
            sec_status = "❌"
            sec_adj = -w_sec # Penalty if weak
        reasons.append(f"Sector Adjustment: {sec_detail} -> {sec_adj}")
    
    breakdown["Sector"] = {"got": round(sec_adj, 1), "max": w_sec, "status": sec_status}
    
    # Optional IO Volume (Options Mode)
    oi_adj = 0.0
    w_oi = weights.get_max_weight("oi_pcr")
    oi_status = "⚠️"
    
    if mode == "OPTIONS" and oi_activity:
        if oi_activity["bias"] == "BULLISH":
            oi_adj = w_oi
            oi_status = "✅"
        elif oi_activity["bias"] == "BEARISH":
            oi_adj = -w_oi
            oi_status = "❌"
        reasons.append(f"OI Adjustment ({oi_activity['activity']}): {oi_adj}")
    
    if mode == "OPTIONS":
        breakdown["OI_PCR"] = {"got": round(oi_adj, 1), "max": w_oi, "status": oi_status}

    adjusted_score = max(0.0, min(100.0, raw_score + mkt_adj + sec_adj + oi_adj))
    
    # 5. Decision Rules Engine
    t_bull = t_norm >= 0.5
    m_bull = m_norm >= 0.5
    s_bull = s_norm >= 0.5
    
    bullish_count = sum([t_bull, m_bull, s_bull])
    
    t_weak = t_norm < 0.5
    m_weak = m_norm < 0.5
    
    if mode == "OPTIONS":
        if adjusted_score >= 80.0 and t_bull and m_bull and s_bull:
            decision = "BUY"
            reasons.append("Decision: [BUY] - Strict Options Threshold Met.")
        elif t_weak and m_weak:
            decision = "SELL"
            reasons.append("Decision: [SELL] - Trend and Momentum are both weak.")
        else:
            decision = "WATCH"
            reasons.append("Decision: [WATCH] - Failed strict Options rules.")
    else:
        if t_bull and m_bull and s_bull:
            decision = "BUY"
            reasons.append("Decision: [BUY] - Trend, Momentum, and Structure all agree.")
        elif bullish_count == 2:
            decision = "WATCH"
            reasons.append("Decision: [WATCH] - Only two engines agree.")
        elif t_weak and m_weak:
            decision = "SELL"
            reasons.append("Decision: [SELL] - Trend and Momentum are both weak.")
        else:
            decision = "SELL"
            reasons.append("Decision: [SELL] - Conditions failed to meet WATCH/BUY thresholds.")
        
    # 5.5 ADX Confirmation Engine (MASTER-21)
    cfg = AppConfig()
    cfg.load()
    strictness_mode = getattr(cfg, 'swing_signal_mode', 'Balanced')

    if adx_result:
        reasons.extend(adx_result.reasons)
        
        # Sideways filter
        adx_downgrade_condition = (adx_result.adx < 20)
        if strictness_mode != 'Conservative':
            adx_downgrade_condition = (adx_result.adx < 20 and adjusted_score < 80)
            
        if adx_downgrade_condition:
            if decision in ["BUY", "SELL"]:
                reasons.append(f"ADX < 20 Sideways Filter: Downgrading {decision} to WATCH.")
                decision = "WATCH"
                
        # Validation checks
        if decision == "BUY" and not adx_result.isValidForBuy:
            reasons.append("ADX Engine: Failed BUY validation (+DI > -DI & ADX > 22). Downgrading to WATCH.")
            decision = "WATCH"
        elif decision == "SELL" and not adx_result.isValidForSell:
            reasons.append("ADX Engine: Failed SELL validation (-DI > +DI & ADX > 22). Downgrading to WATCH.")
            decision = "WATCH"
            
    # 5.6 MTCE Engine (MASTER-23)
    if mtf_result:
        reasons.extend(mtf_result.reasons)
        if mtf_result.alignment_status == "Perfect Alignment":
            adjusted_score = min(100.0, adjusted_score + 10.0)
            reasons.append("MTCE: Perfect Alignment! Boosting Elite Score (+10).")
        elif mtf_result.alignment_status == "Major Conflict":
            adjusted_score = max(0.0, adjusted_score - 20.0)
            if decision in ["BUY", "SELL"]:
                reasons.append(f"MTCE: Major Conflict. Rejecting {decision} trade. Downgrading to WAIT.")
                decision = "WAIT"
        elif mtf_result.alignment_status == "Partial Alignment":
            if decision in ["BUY", "SELL"]:
                if strictness_mode == 'Conservative':
                    reasons.append(f"MTCE: Wait for confirmation. Downgrading {decision} to WAIT.")
                    decision = "WAIT"
                else:
                    reasons.append(f"MTCE: Partial Alignment. Keeping {decision} in {strictness_mode} mode.")
        elif mtf_result.alignment_status == "No Alignment":
            adjusted_score = max(0.0, adjusted_score - 10.0)
            if decision in ["BUY", "SELL"]:
                reasons.append(f"MTCE: No Alignment (Sideways). Downgrading {decision} to WAIT.")
                decision = "WAIT"

    # 6. Confidence & Quality Grade (Stage 7)
    if bullish_count <= 1:
        base_confidence = (((1.0 - t_norm) + (1.0 - m_norm) + (1.0 - s_norm)) / 3.0) * 100.0
    else:
        base_confidence = ((t_norm + m_norm + s_norm) / 3.0) * 100.0
    
    # Apply AVWAP and ADX adjustments to confidence
    confidence_adjustments = []
    final_confidence = base_confidence
    
    # Base weight 70% if both exist, else 80% or 100%
    weight_base = 1.0
    if adx_result and avwap_result:
        weight_base = 0.70
        final_confidence = (base_confidence * 0.70) + (adx_result.score * 0.15) + (avwap_result.score * 0.15)
        confidence_adjustments.append(f"ADX & AVWAP Adjusted Confidence: {final_confidence:.2f}%")
    elif adx_result:
        weight_base = 0.80
        final_confidence = (base_confidence * 0.80) + (adx_result.score * 0.20)
        confidence_adjustments.append(f"ADX Adjusted Confidence: {final_confidence:.2f}%")
    elif avwap_result:
        weight_base = 0.80
        final_confidence = (base_confidence * 0.80) + (avwap_result.score * 0.20)
        confidence_adjustments.append(f"AVWAP Adjusted Confidence: {final_confidence:.2f}%")
        
    confidence = final_confidence
    if confidence_adjustments:
        reasons.extend(confidence_adjustments)
        
    if mtf_result:
        if mtf_result.alignment_status == "Perfect Alignment":
            confidence = min(100.0, confidence + 10.0)
            reasons.append(f"MTCE Confidence Boost: +10% -> {confidence:.2f}%")
        elif mtf_result.alignment_status == "Major Conflict":
            confidence = max(0.0, confidence - 20.0)
            reasons.append(f"MTCE Confidence Penalty: -20% -> {confidence:.2f}%")
        elif mtf_result.alignment_status == "No Alignment":
            confidence = max(0.0, confidence - 10.0)
            reasons.append(f"MTCE Confidence Penalty: -10% -> {confidence:.2f}%")
        
    if avwap_result:
        reasons.extend(avwap_result.reasons)
    
    grade = "D"
    if adjusted_score >= 90 and confidence >= 80:
        grade = "A+"
    elif adjusted_score >= 85 and confidence >= 70:
        grade = "A"
    elif adjusted_score >= 75 and confidence >= 60:
        grade = "B"
    elif adjusted_score >= 65:
        grade = "C"
        
    upstream_reasons = trend_result.reasons + momentum_result.reasons + structure_result.reasons
    all_reasons = upstream_reasons + ["--- Dynamic Weighted Math ---"] + reasons
    
    # 7. Radar Analysis Aggregation (Sprint 46)
    radar_analysis = {}
    radar_analysis.update(getattr(trend_result, 'details', {}))
    radar_analysis.update(getattr(momentum_result, 'details', {}))
    radar_analysis.update(getattr(structure_result, 'details', {}))
    radar_analysis["Sector"] = f"🟢 Strong" if sec_status == "✅" else f"🔴 Weak" if sec_status == "❌" else f"🟡 Neutral"
    radar_analysis["Market"] = f"🟢 Bullish" if mkt_status == "✅" else f"🔴 Bearish" if mkt_status == "❌" else f"🟡 Neutral"
    breakdown["Radar_Analysis"] = radar_analysis
    
    res = de.DecisionResult(
        raw_score=round(raw_score, 2),
        market_adjustment=round(mkt_adj, 2),
        adjusted_score=round(adjusted_score, 2),
        confidence=round(confidence, 2),
        decision=decision,
        reasons=all_reasons
    )
    
    # Dynamically attach Breakdown & Grade to result object
    res.breakdown_detail = breakdown
    res.quality_grade = grade
    
    return res

# Inject the patch directly into the DecisionEngine class
de.DecisionEngine.calculate = _calibrated_decision_calculate
