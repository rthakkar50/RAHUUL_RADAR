"""
Decision Engine module for RAHUUL_RADAR - ENHANCED VERSION
Aggregates technical scores, market state, AND volume confirmation
to generate final trading decisions with proper risk management.

CHANGES FROM ORIGINAL:
1. BUY threshold raised: 50 → 60 (SWING), 50 → 55 (INTRADAY)
2. Volume confirmation MANDATORY for BUY
3. Market bonus capped at +5 (was +10)
4. ADX > 20 required for BUY
5. Stop loss calculation added to decision
6. Confidence minimum 60% for BUY
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any

from utils.logger import get_logger
from core.trend_engine import TrendResult
from core.momentum_engine import MomentumResult
from core.structure_engine import StructureResult
from core.composite_layer import CompositeLayer, CompositeEvaluation

logger = get_logger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS - Centralized thresholds (easy to tweak)
# ═══════════════════════════════════════════════════════════════════════════════

# Score thresholds
BUY_THRESHOLD_SWING = 60.0       # Was 50.0 - More conservative
BUY_THRESHOLD_INTRADAY = 55.0    # Was 50.0 - Slightly lower for intraday
BUY_THRESHOLD_OPTIONS = 70.0     # Unchanged - Already strict
WATCH_THRESHOLD_UPPER = 45.0     # Was 40.0 - Tighter range
WATCH_THRESHOLD_LOWER = 35.0   # Was 40.0 - Tighter range
SELL_THRESHOLD_OPTIONS = 25.0    # Was 20.0 - Earlier exit

# Market bonus cap
MAX_MARKET_BONUS = 5.0           # Was 10.0 - Cap to prevent override
MIN_MARKET_PENALTY = -5.0        # Symmetric penalty

# Volume requirements
MIN_VOLUME_SURGE_RATIO = 1.5     # Volume must be 1.5x average
MIN_ADX_FOR_BUY = 20.0           # Trend strength minimum
MIN_CONFIDENCE_FOR_BUY = 60.0  # Engine agreement minimum

# Stop loss defaults
DEFAULT_SL_PCT_SWING = 0.05      # 5% for swing
DEFAULT_SL_PCT_INTRADAY = 0.02   # 2% for intraday
DEFAULT_SL_PCT_OPTIONS = 0.03   # 3% for options


@dataclass
class MarketState:
    """
    Data structure representing the overall market conditions.
    Used to provide contextual bonuses or penalties to individual stock decisions.
    """
    trend: str
    strength: float
    volatility: float
    market_bias: str
    confidence: float


@dataclass
class VolumeConfirmation:
    """
    NEW: Volume analysis result for trade confirmation.
    """
    is_confirmed: bool = False
    volume_ratio: float = 0.0
    avg_volume: float = 0.0
    current_volume: float = 0.0
    reason: str = ""


@dataclass
class DecisionResult:
    """
    Data structure representing the final actionable decision from the engine.
    ENHANCED: Now includes stop_loss and volume_confirmation.
    """
    raw_score: float
    market_adjustment: float
    adjusted_score: float
    confidence: float
    decision: str
    reasons: List[str] = field(default_factory=list)
    adx_value: float = 0.0
    avwap_status: str = "Neutral"
    mtf_data: Optional[Any] = None
    composite_evaluation: Optional[CompositeEvaluation] = None
    legacy_decision: Optional[str] = None

    # NEW FIELDS
    stop_loss: float = 0.0
    take_profit: float = 0.0
    volume_confirmed: bool = False
    volume_ratio: float = 0.0
    risk_reward_ratio: float = 0.0
    position_size_pct: float = 0.0  # Recommended position size

    # F&O DATA FIELDS
    oi_change_pct: float = 0.0
    pcr: float = 1.0
    max_pain: float = 0.0
    total_oi: int = 0
    fno_bias: str = "NEUTRAL"

    @property
    def total_score(self) -> float:
        """Alias for backward compatibility with ScannerEngine."""
        return self.adjusted_score


class DecisionEngine:
    """
    Engine responsible for aggregating the outputs of all technical engines 
    and overall market state into a final, actionable trading decision.

    ENHANCED VERSION:
    - Stricter thresholds
    - Volume confirmation mandatory
    - Capped market bonus
    - Stop loss calculation
    - Risk-based position sizing
    """

    def __init__(self) -> None:
        """Initializes the DecisionEngine."""
        logger.debug("DecisionEngine (Enhanced) instantiated securely.")
        self.composite_layer = CompositeLayer()

    def _check_volume_confirmation(
        self,
        ohlcv_list: Optional[List] = None,
        min_ratio: float = MIN_VOLUME_SURGE_RATIO
    ) -> VolumeConfirmation:
        """
        NEW: Check if volume confirms the signal.

        Args:
            ohlcv_list: List of OHLCV candles
            min_ratio: Minimum volume surge ratio (default 1.5x)

        Returns:
            VolumeConfirmation with is_confirmed flag
        """
        if not ohlcv_list or len(ohlcv_list) < 20:
            return VolumeConfirmation(
                is_confirmed=False,
                reason="Insufficient volume data (need 20+ candles)"
            )

        try:
            # Calculate average volume (excluding latest candle)
            avg_volume = sum(c.volume for c in ohlcv_list[-20:-1]) / 19
            latest_volume = ohlcv_list[-1].volume

            if avg_volume <= 0:
                return VolumeConfirmation(
                    is_confirmed=False,
                    reason="Average volume is zero"
                )

            volume_ratio = latest_volume / avg_volume

            if volume_ratio >= min_ratio:
                return VolumeConfirmation(
                    is_confirmed=True,
                    volume_ratio=round(volume_ratio, 2),
                    avg_volume=avg_volume,
                    current_volume=latest_volume,
                    reason=f"Volume surge: {volume_ratio:.1f}x average (min: {min_ratio}x)"
                )
            else:
                return VolumeConfirmation(
                    is_confirmed=False,
                    volume_ratio=round(volume_ratio, 2),
                    avg_volume=avg_volume,
                    current_volume=latest_volume,
                    reason=f"Volume weak: {volume_ratio:.1f}x average (need: {min_ratio}x)"
                )

        except Exception as e:
            logger.warning(f"Volume check error: {e}")
            return VolumeConfirmation(
                is_confirmed=False,
                reason=f"Volume check failed: {e}"
            )

    def _calculate_stop_loss(
        self,
        entry_price: float,
        atr: Optional[float] = None,
        mode: str = "SWING",
        structure_low: Optional[float] = None
    ) -> tuple[float, float]:
        """
        NEW: Calculate stop loss and take profit levels.

        Args:
            entry_price: Entry price for the trade
            atr: Average True Range (optional, for ATR-based SL)
            mode: Trading mode (SWING, INTRADAY, OPTIONS)
            structure_low: Recent swing low (optional, for structure-based SL)

        Returns:
            Tuple of (stop_loss, take_profit)
        """
        if mode == "OPTIONS":
            sl_pct = DEFAULT_SL_PCT_OPTIONS
            tp_pct = sl_pct * 2.0  # 1:2 risk-reward
        elif mode == "INTRADAY":
            sl_pct = DEFAULT_SL_PCT_INTRADAY
            tp_pct = sl_pct * 1.5  # 1:1.5 risk-reward
        else:  # SWING
            sl_pct = DEFAULT_SL_PCT_SWING
            tp_pct = sl_pct * 2.0  # 1:2 risk-reward

        # If ATR available, use ATR-based SL (more dynamic)
        if atr and atr > 0:
            sl_amount = atr * 2.0  # 2x ATR
            tp_amount = atr * 4.0  # 4x ATR
        else:
            sl_amount = entry_price * sl_pct
            tp_amount = entry_price * tp_pct

        # If structure low available, use the tighter of the two
        if structure_low and structure_low < entry_price:
            structure_sl = entry_price - (entry_price - structure_low) * 0.9
            stop_loss = max(entry_price - sl_amount, structure_sl)
        else:
            stop_loss = entry_price - sl_amount

        take_profit = entry_price + tp_amount

        return round(stop_loss, 2), round(take_profit, 2)

    def _calculate_position_size(
        self,
        capital: float,
        entry_price: float,
        stop_loss: float,
        max_risk_pct: float = 0.02
    ) -> float:
        """
        NEW: Calculate recommended position size based on risk.

        Args:
            capital: Total trading capital
            entry_price: Entry price
            stop_loss: Stop loss price
            max_risk_pct: Maximum risk per trade (default 2%)

        Returns:
            Recommended position size as percentage of capital
        """
        if stop_loss >= entry_price:
            return 0.0  # Invalid SL

        risk_per_share = entry_price - stop_loss
        risk_amount = capital * max_risk_pct

        if risk_per_share <= 0:
            return 0.0

        num_shares = risk_amount / risk_per_share
        position_value = num_shares * entry_price
        position_pct = (position_value / capital) * 100

        # Cap at 20% of capital per trade
        return min(round(position_pct, 2), 20.0)

    def calculate(
        self,
        trend_result: TrendResult,
        momentum_result: MomentumResult,
        structure_result: StructureResult,
        market_state: Optional[MarketState] = None,
        mode: str = "SWING",
        sector_result = None,
        oi_activity = None,
        adx_result = None,
        avwap_result = None,
        mtf_result = None,
        composite_rs = None,
        composite_enabled: bool = False,
        # NEW PARAMETERS
        ohlcv_list: Optional[List] = None,
        entry_price: Optional[float] = None,
        capital: Optional[float] = None,
        atr: Optional[float] = None,
        structure_low: Optional[float] = None,
    ) -> DecisionResult:
        """
        Calculates the final trading decision by mathematically aggregating sub-engine results.

        ENHANCED: Now includes volume confirmation, stop loss, and position sizing.
        """
        reasons: List[str] = []

        # ═══════════════════════════════════════════════════════════════════
        # 1. Base Scores Extraction
        # ═══════════════════════════════════════════════════════════════════
        trend_score = trend_result.score
        momentum_score = momentum_result.score
        structure_score = structure_result.score

        reasons.append(f"Trend Base Score: {trend_score}")
        reasons.append(f"Momentum Base Score: {momentum_score}")
        reasons.append(f"Structure Base Score: {structure_score}")

        # Calculate Raw Score
        raw_score = float(trend_score + momentum_score + structure_score)

        # ═══════════════════════════════════════════════════════════════════
        # 2. Calculate Confidence (Agreement between engines)
        # ═══════════════════════════════════════════════════════════════════
        t_dir = (trend_score / 30.0) * 2.0 - 1.0
        m_dir = (momentum_score / 25.0) * 2.0 - 1.0
        s_dir = (structure_score / 25.0) * 2.0 - 1.0

        agreement = abs(t_dir + m_dir + s_dir) / 3.0
        confidence = min(100.0, max(0.0, agreement * 100.0))

        reasons.append(f"Engine Agreement: {confidence:.1f}%")

        # ═══════════════════════════════════════════════════════════════════
        # 3. Market State Bonus Application (CAPPED)
        # ═══════════════════════════════════════════════════════════════════
        market_bonus = 0.0

        if market_state:
            # CAP the bonus to prevent override of weak signals
            raw_bonus = market_state.strength / 10.0
            capped_bonus = min(abs(raw_bonus), MAX_MARKET_BONUS)

            if market_state.market_bias in ["BULLISH", "STRONG_BULL"]:
                market_bonus = capped_bonus
                reasons.append(f"Bullish Market Context Bonus: +{market_bonus:.2f} (capped from {raw_bonus:.2f})")
            elif market_state.market_bias in ["BEARISH", "STRONG_BEAR"]:
                market_bonus = -capped_bonus
                reasons.append(f"Bearish Market Context Penalty: {market_bonus:.2f} (capped from {-raw_bonus:.2f})")
            else:
                reasons.append("Neutral Market Context: No bonus applied")
        else:
            reasons.append("No broader MarketState provided. Operating in isolation.")

        # ═══════════════════════════════════════════════════════════════════
        # 4. Final Aggregation
        # ═══════════════════════════════════════════════════════════════════
        adjusted_score = raw_score + market_bonus
        adjusted_score = max(0.0, min(100.0, adjusted_score))

        # ═══════════════════════════════════════════════════════════════════
        # 5. NEW: Volume Confirmation Check
        # ═══════════════════════════════════════════════════════════════════
        volume_check = self._check_volume_confirmation(ohlcv_list)
        volume_confirmed = volume_check.is_confirmed

        if volume_confirmed:
            reasons.append(f"✅ Volume Confirmed: {volume_check.reason}")
        else:
            reasons.append(f"⚠️ Volume Not Confirmed: {volume_check.reason}")

        # ═══════════════════════════════════════════════════════════════════
        # 6. NEW: ADX Check for trend strength
        # ═══════════════════════════════════════════════════════════════════
        adx_value = adx_result.adx if adx_result else 0.0
        adx_ok = adx_value >= MIN_ADX_FOR_BUY

        if adx_ok:
            reasons.append(f"✅ ADX Strong: {adx_value:.1f} (min: {MIN_ADX_FOR_BUY})")
        else:
            reasons.append(f"⚠️ ADX Weak: {adx_value:.1f} (min: {MIN_ADX_FOR_BUY})")

        # ═══════════════════════════════════════════════════════════════════
        # 7. ENHANCED Decision Matrix with STRICTER thresholds
        # ═══════════════════════════════════════════════════════════════════
        decision = "WATCH"

        if mode == "OPTIONS":
            if adjusted_score >= BUY_THRESHOLD_OPTIONS and volume_confirmed and adx_ok and confidence >= MIN_CONFIDENCE_FOR_BUY:
                decision = "BUY"
                reasons.append(f"🟢 Score ({adjusted_score:.1f}) >= {BUY_THRESHOLD_OPTIONS} + Volume + ADX + Confidence → [BUY]")
            elif adjusted_score <= SELL_THRESHOLD_OPTIONS:
                decision = "SELL"
                reasons.append(f"🔴 Score ({adjusted_score:.1f}) <= {SELL_THRESHOLD_OPTIONS} → [SELL]")
            else:
                decision = "WATCH"
                reasons.append(f"🟡 Score ({adjusted_score:.1f}) between {SELL_THRESHOLD_OPTIONS}-{BUY_THRESHOLD_OPTIONS} → [WATCH]")

        elif mode == "INTRADAY":
            if adjusted_score >= BUY_THRESHOLD_INTRADAY and volume_confirmed and adx_ok and confidence >= MIN_CONFIDENCE_FOR_BUY:
                decision = "BUY"
                reasons.append(f"🟢 Score ({adjusted_score:.1f}) >= {BUY_THRESHOLD_INTRADAY} + Volume + ADX + Confidence → [BUY]")
            elif adjusted_score >= WATCH_THRESHOLD_LOWER:
                decision = "WATCH"
                reasons.append(f"🟡 Score ({adjusted_score:.1f}) in {WATCH_THRESHOLD_LOWER}-{BUY_THRESHOLD_INTRADAY} → [WATCH]")
            else:
                decision = "SELL"
                reasons.append(f"🔴 Score ({adjusted_score:.1f}) below {WATCH_THRESHOLD_LOWER} → [SELL]")
        else:  # SWING (default)
            if adjusted_score >= BUY_THRESHOLD_SWING and volume_confirmed and adx_ok and confidence >= MIN_CONFIDENCE_FOR_BUY:
                decision = "BUY"
                reasons.append(f"🟢 Score ({adjusted_score:.1f}) >= {BUY_THRESHOLD_SWING} + Volume + ADX + Confidence → [BUY]")
            elif adjusted_score >= WATCH_THRESHOLD_LOWER:
                decision = "WATCH"
                reasons.append(f"🟡 Score ({adjusted_score:.1f}) in {WATCH_THRESHOLD_LOWER}-{BUY_THRESHOLD_SWING} → [WATCH]")
            else:
                decision = "SELL"
                reasons.append(f"🔴 Score ({adjusted_score:.1f}) below {WATCH_THRESHOLD_LOWER} → [SELL]")

        # ═══════════════════════════════════════════════════════════════════
# 8b. NEW: F&O OI/PCR Analysis
# ═══════════════════════════════════════════════════════════════════
        oi_change_pct = 0.0
        pcr = 1.0
        max_pain = 0.0
        total_oi = 0
        fno_bias = "NEUTRAL"

        if oi_activity and isinstance(oi_activity, dict):
            oi_change_pct = oi_activity.get("oi_change_pct", 0)
            pcr = oi_activity.get("pcr", 1.0)
            max_pain = oi_activity.get("max_pain", 0)
            total_oi = oi_activity.get("total_oi", 0)
            
            # Determine F&O bias
            if pcr < 0.7:
                fno_bias = "BULLISH_EXTREME"
            elif pcr < 1.0:
                fno_bias = "BULLISH"
            elif pcr > 1.3:
                fno_bias = "BEARISH_EXTREME"
            elif pcr > 1.0:
                fno_bias = "BEARISH"
            
            reasons.append(f"F&O Data: OI={total_oi:,}, OIΔ={oi_change_pct:.1f}%, PCR={pcr:.2f}, Bias={fno_bias}")
            
            # F&O Score Adjustment
            if abs(oi_change_pct) >= 10:
                adjusted_score += 5  # Strong OI buildup
                reasons.append("F&O Bonus: Strong OI buildup (+5)")
            elif abs(oi_change_pct) >= 5:
                adjusted_score += 2  # Moderate OI buildup
                reasons.append("F&O Bonus: Moderate OI buildup (+2)")
            
            # PCR Contrarian Filter
            if decision == "BUY" and pcr > 1.3:
                decision = "WATCH"
                reasons.append("[F&O VETO] PCR > 1.3 (extreme bearish) - Downgraded to WATCH")
            elif decision == "SELL" and pcr < 0.7:
                decision = "WATCH"
                reasons.append("[F&O VETO] PCR < 0.7 (extreme bullish) - Downgraded to WATCH")

        # 8. NEW: Calculate Stop Loss and Take Profit
        # ═══════════════════════════════════════════════════════════════════
        stop_loss = 0.0
        take_profit = 0.0
        position_size_pct = 0.0
        risk_reward = 0.0

        if decision == "BUY" and entry_price and entry_price > 0:
            stop_loss, take_profit = self._calculate_stop_loss(
                entry_price=entry_price,
                atr=atr,
                mode=mode,
                structure_low=structure_low
            )

            if capital and capital > 0:
                position_size_pct = self._calculate_position_size(
                    capital=capital,
                    entry_price=entry_price,
                    stop_loss=stop_loss
                )

            if stop_loss > 0 and take_profit > 0:
                risk_reward = round((take_profit - entry_price) / (entry_price - stop_loss), 2)

            reasons.append(f"🛡️ Stop Loss: ₹{stop_loss} | 🎯 Take Profit: ₹{take_profit}")
            reasons.append(f"📊 Risk-Reward: 1:{risk_reward} | Position: {position_size_pct}% of capital")

        # ═══════════════════════════════════════════════════════════════════
        # 9. Console Output (using logger instead of print)
        # ═══════════════════════════════════════════════════════════════════
        logger.info("=" * 50)
        logger.info("DECISION ENGINE OUTPUT")
        logger.info(f"Trend Score:       {trend_score}")
        logger.info(f"Momentum Score:    {momentum_score}")
        logger.info(f"Structure Score:   {structure_score}")
        logger.info(f"Raw Score:         {raw_score}")
        logger.info(f"Market Adjustment: {market_bonus:.2f}")
        logger.info(f"Adjusted Score:    {adjusted_score:.2f}")
        logger.info(f"Volume Confirmed:  {volume_confirmed}")
        logger.info(f"ADX:               {adx_value:.1f} (min: {MIN_ADX_FOR_BUY})")
        logger.info(f"Confidence:        {confidence:.1f}%")
        logger.info(f"Decision:          {decision}")
        if stop_loss > 0:
            logger.info(f"Stop Loss:         ₹{stop_loss}")
            logger.info(f"Take Profit:       ₹{take_profit}")
        logger.info("=" * 50)

        # ═══════════════════════════════════════════════════════════════════
        # 10. Combine all upstream reasons
        # ═══════════════════════════════════════════════════════════════════
        upstream_reasons = trend_result.reasons + momentum_result.reasons + structure_result.reasons
        all_reasons = upstream_reasons + ["--- Decision Math ---"] + reasons

        # ═══════════════════════════════════════════════════════════════════
        # 11. Composite Layer Evaluation
        # ═══════════════════════════════════════════════════════════════════
        composite_evaluation = None
        if composite_enabled:
            composite_evaluation = self.composite_layer.evaluate(composite_rs, decision)
            all_reasons.append("--- Institutional Quality Overlay ---")
            all_reasons.extend(composite_evaluation.reasons)

        # ═══════════════════════════════════════════════════════════════════
        # 12. Return Enhanced DecisionResult
        # ═══════════════════════════════════════════════════════════════════
        return DecisionResult(
            raw_score=round(raw_score, 2),
            market_adjustment=round(market_bonus, 2),
            adjusted_score=round(adjusted_score, 2),
            confidence=round(confidence, 2),
            decision=decision,
            reasons=all_reasons,
            adx_value=adx_value,
            avwap_status=avwap_result.position if avwap_result else "Neutral",
            mtf_data=mtf_result,
            composite_evaluation=composite_evaluation,
            # NEW FIELDS
            stop_loss=stop_loss,
            take_profit=take_profit,
            volume_confirmed=volume_confirmed,
            volume_ratio=volume_check.volume_ratio,
            risk_reward_ratio=risk_reward,
            position_size_pct=position_size_pct,
            # F&O DATA
            oi_change_pct=oi_change_pct,
            pcr=pcr,
            max_pain=max_pain,
            total_oi=total_oi,
            fno_bias=fno_bias
        )
