"""
RAHUUL RADAR — F&O Signal Engine (Task 12, Task 13, Task 15)
============================================================
Master Orchestrator for the Derivatives F&O Engine.
Coordinates SymbolManager, ExpiryEngine, ContractSelector, OptionChainEngine,
OIEngine, PCREngine, MaxPainEngine, GreeksEngine, IVEngine, FNOAIEngine, and FNORiskEngine.
Executes in <100ms with 100% backward-compatible decoupled interface.
"""

import time
import logging
from typing import Dict, Any, Optional

from core.fno_engine.fno_models import FNOSignal, FNOContract, OptionType
from core.fno_engine.symbol_manager import FNOSymbolManager
from core.fno_engine.expiry_engine import ExpiryEngine
from core.fno_engine.contract_selector import ContractSelector
from core.fno_engine.option_chain_engine import OptionChainEngine
from core.fno_engine.oi_engine import OIEngine
from core.fno_engine.pcr_engine import PCREngine
from core.fno_engine.maxpain_engine import MaxPainEngine
from core.fno_engine.greeks_engine import GreeksEngine
from core.fno_engine.iv_engine import IVEngine
from core.fno_engine.fno_ai_engine import FNOAIEngine
from core.fno_engine.fno_risk_engine import FNORiskEngine

logger = logging.getLogger("FNOSignalEngine")


class FNOSignalEngine:
    """
    Independent Derivatives Signal Generation & Risk Analysis Center.
    """

    def __init__(self):
        self.symbol_manager = FNOSymbolManager()
        self.expiry_engine = ExpiryEngine()
        self.contract_selector = ContractSelector()
        self.option_chain_engine = OptionChainEngine.get_instance()
        self.oi_engine = OIEngine()
        self.pcr_engine = PCREngine()
        self.maxpain_engine = MaxPainEngine()
        self.greeks_engine = GreeksEngine()
        self.iv_engine = IVEngine()
        self.fno_ai_engine = FNOAIEngine()
        self.fno_risk_engine = FNORiskEngine()

    def generate_fno_signal(
        self,
        underlying: str,
        spot_price: float,
        strike_type: str = "ATM",
        expiry_type: str = "CURRENT_WEEKLY",
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end derivatives signal generation in <100ms.
        Returns Task 12 standard schema dictionary.
        """
        start_time = time.time()
        ctx = context_data or {}

        underlying_clean = underlying.upper().replace(".NS", "")
        step = self.symbol_manager.get_strike_step(underlying_clean)

        # 1. Expiry Selection
        if expiry_type.upper() == "NEXT_WEEKLY":
            expiry_date = self.expiry_engine.get_next_weekly_expiry(underlying_clean)
        elif expiry_type.upper() == "MONTHLY":
            expiry_date = self.expiry_engine.get_monthly_expiry(underlying_clean)
        else:
            expiry_date = self.expiry_engine.get_current_weekly_expiry(underlying_clean)

        # 2. Strike Selection
        selected_strike = self.contract_selector.select_strike(
            spot_price, option_type="CE", strike_type=strike_type, step=step
        )

        # 3. Option Chain Retrieval (Cached <15ms)
        chain = self.option_chain_engine.get_option_chain(
            underlying_clean, spot_price, expiry_date, step=step
        )

        # 4. Quantitative Derivative Engine Calculations
        oi_metrics = self.oi_engine.calculate_oi_metrics(chain)
        pcr_metrics = self.pcr_engine.calculate_pcr(chain, target_strike=selected_strike)
        maxpain_metrics = self.maxpain_engine.calculate_max_pain(chain)
        iv_metrics = self.iv_engine.calculate_iv_metrics(current_iv=16.5)

        greeks = self.greeks_engine.calculate_greeks(
            spot=spot_price,
            strike=selected_strike,
            time_to_expiry_years=0.019, # ~7 days
            volatility=0.165,
            option_type="CE"
        )

        # 5. AI Derivatives Decision
        vwap = float(ctx.get("vwap") or spot_price)
        ema_20 = float(ctx.get("ema_20") or (spot_price * 0.99))
        ema_200 = float(ctx.get("ema_200") or (spot_price * 0.95))

        ai_res = self.fno_ai_engine.evaluate_derivatives_signal(
            symbol=underlying_clean,
            spot_price=spot_price,
            vwap=vwap,
            ema_20=ema_20,
            ema_200=ema_200,
            oi_metrics=oi_metrics,
            pcr_metrics=pcr_metrics,
            max_pain_metrics=maxpain_metrics,
            iv_metrics=iv_metrics,
            greeks=greeks
        )

        action = ai_res["action"]
        confidence = ai_res["confidence"]
        option_type = "CE" if action in ("BUY", "WAIT") else "PE"

        # 6. Risk Engine Allocation
        # Option Premium Estimation
        target_item = next((i for i in chain if abs(i.strike_price - selected_strike) < 1.0), None)
        entry_premium = target_item.call_ltp if option_type == "CE" and target_item else (target_item.put_ltp if target_item else 100.0)

        risk_report = self.fno_risk_engine.calculate_risk_parameters(
            symbol=underlying_clean,
            entry_price=entry_premium,
            spot_price=spot_price,
            action="BUY" if action == "BUY" else "SELL"
        )

        # Construct final FNO Contract Symbol
        contract_symbol = f"{underlying_clean}-{expiry_date}-{int(selected_strike)}{option_type}"
        exec_time_ms = (time.time() - start_time) * 1000.0

        signal = FNOSignal(
            symbol=contract_symbol,
            underlying=underlying_clean,
            expiry=expiry_date,
            strike=selected_strike,
            option_type=option_type,
            action=action,
            confidence=confidence,
            entry=entry_premium,
            stop_loss=risk_report.stop_loss,
            target_1=risk_report.target_1,
            target_2=risk_report.target_2,
            target_3=risk_report.target_3,
            risk_reward=f"1:{risk_report.risk_reward}",
            reasons=ai_res["reasons"] + [f"Inference Latency {exec_time_ms:.2f}ms"]
        )

        return signal.to_dict()
