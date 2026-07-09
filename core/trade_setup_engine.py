from dataclasses import dataclass, field
from typing import List, Optional

from utils.logger import get_logger
from core.models import ScanResult
from market.data_provider import OHLCV

logger = get_logger(__name__)

@dataclass
class TradeSetup:
    """
    Data structure representing a fully calculated trade setup.
    """
    symbol: str
    signal: str
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    risk: float
    reward: float
    risk_reward_ratio: float
    holding_type: str
    reasons: List[str] = field(default_factory=list)

    def display_console(self):
        print("\n" + "="*40)
        print(f"🌟 TODAY'S BEST TRADE: {self.symbol} 🌟")
        print("="*40)
        print(f"Signal:       {self.signal}")
        print(f"Entry Price:  {self.entry_price:.2f}")
        print(f"Stop Loss:    {self.stop_loss:.2f}")
        print(f"Target 1:     {self.target_1:.2f} (1R)")
        print(f"Target 2:     {self.target_2:.2f} (2R)")
        print(f"Target 3:     {self.target_3:.2f} (3R)")
        print(f"Risk/Reward:  {self.risk_reward_ratio:.2f}")
        print("Reasons:")
        for r in self.reasons:
            print(f"  - {r}")
        print("="*40 + "\n")


class TradeSetupEngine:
    """
    Evaluates actionable signals to build precise risk-reward execution plans.
    """
    def __init__(self, swing_lookback: int = 5, buffer_pct: float = 0.001):
        self.swing_lookback = swing_lookback
        self.buffer_pct = buffer_pct

    def generate_setup(self, scan_result: ScanResult, ohlcv_list: List[OHLCV], mode: str = "SWING") -> Optional[TradeSetup]:
        reasons = []
        
        # Extract decision string robustly
        decision = getattr(scan_result.signal, 'value', str(scan_result.signal))
        
        if decision == "WATCH":
            return None
            
        if not ohlcv_list or len(ohlcv_list) < self.swing_lookback + 1:
            logger.warning(f"Insufficient OHLCV data to generate setup for {scan_result.symbol}")
            return None
            
        # Get recent candles
        recent_candles = ohlcv_list[-self.swing_lookback:]
        latest_candle = ohlcv_list[-1]
        
        buffer_amount = latest_candle.close * self.buffer_pct
        
        entry_price = 0.0
        stop_loss = 0.0
        
        # Calculate VMA (10-period) and ATR (14-period)
        vma_10 = sum(c.volume for c in ohlcv_list[-10:]) / min(10, len(ohlcv_list)) if ohlcv_list else 0
        
        atr = 0
        if len(ohlcv_list) > 14:
            tr_list = []
            for i in range(len(ohlcv_list) - 14, len(ohlcv_list)):
                curr = ohlcv_list[i]
                prev = ohlcv_list[i-1]
                tr = max(curr.high - curr.low, abs(curr.high - prev.close), abs(curr.low - prev.close))
                tr_list.append(tr)
            atr = sum(tr_list) / len(tr_list)
        else:
            atr = latest_candle.high - latest_candle.low
            
        # Volume Validation for Options Mode
        if mode == "OPTIONS":
            if latest_candle.volume < vma_10:
                reasons.append(f"REJECTED: Low Volume ({latest_candle.volume} < {vma_10:.0f}). Unsafe for Options.")
                decision = "WATCH"
        
        if decision == "BUY":
            # Entry = Previous Candle High + Buffer
            entry_price = latest_candle.high + buffer_amount
            # Stop Loss
            if mode == "OPTIONS":
                stop_loss = entry_price - (1.5 * atr)
                reasons.append(f"Stop Loss based on 1.5x ATR ({stop_loss:.2f}).")
            else:
                stop_loss = min(c.low for c in recent_candles)
                reasons.append(f"Stop Loss based on {self.swing_lookback}-period Swing Low ({stop_loss:.2f}).")
            
            if stop_loss >= entry_price:
                # Fallback if anomaly
                stop_loss = entry_price * 0.98
                
            risk = entry_price - stop_loss
            
            if mode == "OPTIONS":
                target_1 = entry_price + (risk * 1.0)
                target_2 = entry_price + (risk * 1.5)
                target_3 = entry_price + (risk * 2.0)
            else:
                target_1 = entry_price + (risk * 1.0)
                target_2 = entry_price + (risk * 2.0)
                target_3 = entry_price + (risk * 3.0)
            
            # For Risk/Reward check, we evaluate against Target 2 (a standard minimum swing objective)
            reward = target_2 - entry_price 
            
            reasons.append(f"Entry based on High break ({latest_candle.high:.2f}) + {self.buffer_pct*100}% buffer.")
            
        elif decision == "SELL":
            # Entry = Previous Candle Low - Buffer
            entry_price = latest_candle.low - buffer_amount
            # Stop Loss
            if mode == "OPTIONS":
                stop_loss = entry_price + (1.5 * atr)
                reasons.append(f"Stop Loss based on 1.5x ATR ({stop_loss:.2f}).")
            else:
                stop_loss = max(c.high for c in recent_candles)
                reasons.append(f"Stop Loss based on {self.swing_lookback}-period Swing High ({stop_loss:.2f}).")
            
            if stop_loss <= entry_price:
                stop_loss = entry_price * 1.02
                
            risk = stop_loss - entry_price
            
            if mode == "OPTIONS":
                target_1 = entry_price - (risk * 1.0)
                target_2 = entry_price - (risk * 1.5)
                target_3 = entry_price - (risk * 2.0)
            else:
                target_1 = entry_price - (risk * 1.0)
                target_2 = entry_price - (risk * 2.0)
                target_3 = entry_price - (risk * 3.0)
            
            # For Risk/Reward check, we evaluate against Target 2
            reward = entry_price - target_2
            
            reasons.append(f"Entry based on Low break ({latest_candle.low:.2f}) - {self.buffer_pct*100}% buffer.")
            
        else:
            return None
            
        risk_reward_ratio = reward / risk if risk > 0 else 0.0
        
        # Filter condition: If Risk Reward < 1.5, Reject setup (for Swing). For Options, check is relaxed.
        min_rr = 1.0 if mode == "OPTIONS" else 1.5
        if risk_reward_ratio < min_rr:
            reasons.append(f"REJECTED: Risk/Reward ({risk_reward_ratio:.2f}) < {min_rr} minimum threshold.")
            decision = "WATCH"
            # Return modified setup but technically it's a WATCH now. 
            # The prompt says "Reject setup, Convert to WATCH"
            # We can still return the setup but with the signal changed to WATCH so the user can inspect it.
            
        setup = TradeSetup(
            symbol=scan_result.symbol,
            signal=decision,
            entry_price=round(entry_price, 2),
            stop_loss=round(stop_loss, 2),
            target_1=round(target_1, 2),
            target_2=round(target_2, 2),
            target_3=round(target_3, 2),
            risk=round(risk, 2),
            reward=round(reward, 2),
            risk_reward_ratio=round(risk_reward_ratio, 2),
            holding_type=mode,
            reasons=reasons
        )
        
        return setup
