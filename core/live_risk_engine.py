"""
RAHUUL RADAR — Sprint M6: Paytm Live Trading Risk Engine
=========================================================
Production-grade risk management that validates every live order BEFORE execution.
No scanner modifications. No AI engine modifications. No Order Engine logic changes.
"""

import os
import json
import logging
import sqlite3
import uuid
import threading
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, field, asdict


logger = logging.getLogger("RiskEngine")


# ─────────────────────────────────────────────────────────────────────────────
# Enums & Result Types
# ─────────────────────────────────────────────────────────────────────────────

class RiskDecision(str, Enum):
    APPROVED  = "APPROVED"
    REJECTED  = "REJECTED"
    REDUCED   = "REDUCED"   # Approved but at a lower quantity


class SizingMethod(str, Enum):
    FIXED_QUANTITY = "FIXED_QUANTITY"
    FIXED_CAPITAL  = "FIXED_CAPITAL"
    RISK_PCT       = "RISK_PCT"
    ATR_BASED      = "ATR_BASED"
    MAX_EXPOSURE   = "MAX_EXPOSURE"


@dataclass
class OrderRiskRequest:
    symbol: str
    action: str                   # BUY | SELL
    quantity: int
    price: float
    stop_loss: float = 0.0
    atr: float = 0.0
    sector: str = "GENERAL"
    product: str = "I"            # I=Intraday, C=Delivery
    order_type: str = "MARKET"
    sizing_method: str = SizingMethod.FIXED_QUANTITY


@dataclass
class RiskCheckResult:
    decision: str                 # RiskDecision value
    approved_quantity: int
    reasons: List[str]            = field(default_factory=list)
    warnings: List[str]           = field(default_factory=list)
    position_size_data: Dict      = field(default_factory=dict)
    risk_report: Dict             = field(default_factory=dict)

    @property
    def is_approved(self) -> bool:
        return self.decision in (RiskDecision.APPROVED, RiskDecision.REDUCED)


# ─────────────────────────────────────────────────────────────────────────────
# Risk Configuration (loaded from config.json)
# ─────────────────────────────────────────────────────────────────────────────

class RiskConfig:
    """Loads and validates risk configuration from config.json."""

    DEFAULTS = {
        # Daily protection
        "daily_loss_limit":          5000.0,   # ₹ absolute
        "daily_profit_target":       15000.0,
        "max_consecutive_losses":    3,
        "max_open_trades":           5,
        "max_orders_per_day":        20,

        # Exposure
        "total_exposure_limit_pct":  80.0,     # % of capital
        "sector_exposure_limit_pct": 30.0,     # % of capital per sector
        "intraday_margin_pct":       20.0,     # 5x leverage
        "delivery_margin_pct":       100.0,    # 1x, full cash

        # Position sizing
        "capital":                   1000000.0,
        "risk_pct":                  1.0,       # % of capital per trade
        "max_position_size_pct":     10.0,      # cap per single trade

        # Kill switch
        "kill_switch_active":        False,
        "auto_trading_enabled":      True,
    }

    def __init__(self, config_path: str = "config.json"):
        self._data: Dict = {}
        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    raw = json.load(f)
                    self._data = raw.get("risk_engine", raw)  # support nested "risk_engine" block
        except Exception as e:
            logger.warning(f"RiskConfig could not read {config_path}: {e}")

    def get(self, key: str, default=None):
        val = self._data.get(key, self.DEFAULTS.get(key, default))
        try:
            return type(self.DEFAULTS[key])(val) if key in self.DEFAULTS else val
        except Exception:
            return self.DEFAULTS.get(key, default)

    @property
    def capital(self) -> float:        return self.get("capital")
    @property
    def risk_pct(self) -> float:       return self.get("risk_pct")
    @property
    def daily_loss_limit(self) -> float:    return self.get("daily_loss_limit")
    @property
    def daily_profit_target(self) -> float: return self.get("daily_profit_target")
    @property
    def max_consecutive_losses(self) -> int:return self.get("max_consecutive_losses")
    @property
    def max_open_trades(self) -> int:       return self.get("max_open_trades")
    @property
    def max_orders_per_day(self) -> int:    return self.get("max_orders_per_day")
    @property
    def total_exposure_limit_pct(self) -> float: return self.get("total_exposure_limit_pct")
    @property
    def sector_exposure_limit_pct(self) -> float:return self.get("sector_exposure_limit_pct")
    @property
    def kill_switch_active(self) -> bool:   return bool(self.get("kill_switch_active"))
    @property
    def auto_trading_enabled(self) -> bool: return bool(self.get("auto_trading_enabled"))


# ─────────────────────────────────────────────────────────────────────────────
# Daily State Tracker (in-memory + SQLite persistence)
# ─────────────────────────────────────────────────────────────────────────────

class DailyRiskTracker:
    """
    Thread-safe daily state for P&L, order counts, consecutive losses,
    open positions, and sector exposure tracking.
    """
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, db_path: str = "data/risk_state.db") -> "DailyRiskTracker":
        with cls._lock:
            if cls._instance is None:
                cls._instance = DailyRiskTracker(db_path)
        return cls._instance

    def __init__(self, db_path: str = "data/risk_state.db"):
        self._lock = threading.Lock()
        self.db_path = db_path
        self._today = str(date.today())

        # In-memory state for the current session
        self.daily_realized_pnl: float = 0.0
        self.orders_today: int = 0
        self.consecutive_losses: int = 0
        self.open_positions: Dict[str, Dict] = {}      # symbol -> {qty, entry, sl, sector}
        self.pending_order_keys: set = set()           # dedup set: "SYMBOL-ACTION-QTY-PRICE"
        self.executed_order_ids: set = set()
        self.kill_switch: bool = False
        self.auto_trading: bool = True

        self._init_db()
        self._load_today_from_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS daily_state (
                trade_date TEXT PRIMARY KEY,
                realized_pnl REAL DEFAULT 0.0,
                orders_count INTEGER DEFAULT 0,
                consecutive_losses INTEGER DEFAULT 0,
                kill_switch INTEGER DEFAULT 0,
                auto_trading INTEGER DEFAULT 1
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS open_positions (
                symbol TEXT PRIMARY KEY,
                trade_date TEXT,
                qty INTEGER,
                entry_price REAL,
                stop_loss REAL,
                sector TEXT DEFAULT 'GENERAL',
                product TEXT DEFAULT 'I'
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS order_events (
                event_id TEXT PRIMARY KEY,
                trade_date TEXT,
                timestamp TEXT,
                symbol TEXT,
                action TEXT,
                quantity INTEGER,
                price REAL,
                result TEXT,
                pnl REAL DEFAULT 0.0
            )
        """)
        conn.commit()
        conn.close()

    def _load_today_from_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            c.execute("SELECT * FROM daily_state WHERE trade_date = ?", (self._today,))
            row = c.fetchone()
            if row:
                self.daily_realized_pnl  = float(row["realized_pnl"])
                self.orders_today        = int(row["orders_count"])
                self.consecutive_losses  = int(row["consecutive_losses"])
                self.kill_switch         = bool(row["kill_switch"])
                self.auto_trading        = bool(row["auto_trading"])

            c.execute("SELECT * FROM open_positions WHERE trade_date = ?", (self._today,))
            for r in c.fetchall():
                self.open_positions[r["symbol"]] = {
                    "qty":         int(r["qty"]),
                    "entry_price": float(r["entry_price"]),
                    "stop_loss":   float(r["stop_loss"]),
                    "sector":      r["sector"],
                    "product":     r["product"],
                }
            conn.close()
        except Exception as e:
            logger.warning(f"DailyRiskTracker could not load from DB: {e}")

    def _persist_daily_state(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO daily_state
                (trade_date, realized_pnl, orders_count, consecutive_losses, kill_switch, auto_trading)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self._today,
                self.daily_realized_pnl,
                self.orders_today,
                self.consecutive_losses,
                int(self.kill_switch),
                int(self.auto_trading),
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to persist daily risk state: {e}")

    # ── Public API ────────────────────────────────────────────────────────────

    def register_order_attempt(self, symbol: str, action: str, qty: int, price: float):
        with self._lock:
            self.orders_today += 1
            self._persist_daily_state()

    def register_order_executed(self, symbol: str, action: str, qty: int,
                                 price: float, sl: float = 0.0,
                                 sector: str = "GENERAL", product: str = "I"):
        """Called after a live order is successfully placed."""
        with self._lock:
            eid = f"EVT-{uuid.uuid4().hex[:10].upper()}"
            if action.upper() == "BUY":
                self.open_positions[symbol] = {
                    "qty": qty,
                    "entry_price": price,
                    "stop_loss": sl,
                    "sector": sector,
                    "product": product,
                }
                # Persist position
                try:
                    conn = sqlite3.connect(self.db_path)
                    c = conn.cursor()
                    c.execute("""
                        INSERT OR REPLACE INTO open_positions
                        (symbol, trade_date, qty, entry_price, stop_loss, sector, product)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (symbol, self._today, qty, price, sl, sector, product))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logger.error(f"Failed to persist open position: {e}")

            elif action.upper() == "SELL" and symbol in self.open_positions:
                pos = self.open_positions.pop(symbol, {})
                pnl = (price - pos.get("entry_price", price)) * qty
                self.daily_realized_pnl += pnl
                if pnl < 0:
                    self.consecutive_losses += 1
                else:
                    self.consecutive_losses = 0
                try:
                    conn = sqlite3.connect(self.db_path)
                    c = conn.cursor()
                    c.execute("DELETE FROM open_positions WHERE symbol = ?", (symbol,))
                    c.execute("""
                        INSERT INTO order_events (event_id, trade_date, timestamp, symbol, action, quantity, price, result, pnl)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (eid, self._today, datetime.now().isoformat(), symbol, action, qty, price,
                          "WIN" if pnl >= 0 else "LOSS", round(pnl, 2)))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logger.error(f"Failed to record exit event: {e}")

            self._persist_daily_state()

    def make_dedup_key(self, symbol: str, action: str, qty: int, price: float) -> str:
        rounded_price = round(price, 1)
        return f"{symbol.upper()}-{action.upper()}-{qty}-{rounded_price}"

    def is_duplicate(self, symbol: str, action: str, qty: int, price: float) -> bool:
        with self._lock:
            key = self.make_dedup_key(symbol, action, qty, price)
            return key in self.pending_order_keys

    def lock_order(self, symbol: str, action: str, qty: int, price: float) -> str:
        with self._lock:
            key = self.make_dedup_key(symbol, action, qty, price)
            self.pending_order_keys.add(key)
            return key

    def release_order_lock(self, key: str):
        with self._lock:
            self.pending_order_keys.discard(key)

    def activate_kill_switch(self):
        with self._lock:
            self.kill_switch = True
            self.auto_trading = False
            self._persist_daily_state()
            logger.critical("🔴 KILL SWITCH ACTIVATED — All trading halted.")

    def deactivate_kill_switch(self):
        with self._lock:
            self.kill_switch = False
            self.auto_trading = True   # re-enable trading together with kill switch reset
            self._persist_daily_state()
            logger.info("🟢 Kill switch deactivated. Auto trading re-enabled.")

    def disable_auto_trading(self):
        with self._lock:
            self.auto_trading = False
            self._persist_daily_state()

    def enable_auto_trading(self):
        with self._lock:
            self.auto_trading = True
            self._persist_daily_state()

    @property
    def open_trade_count(self) -> int:
        return len(self.open_positions)

    @property
    def total_open_exposure(self) -> float:
        return sum(
            p.get("entry_price", 0.0) * p.get("qty", 0)
            for p in self.open_positions.values()
        )

    def sector_exposure(self, sector: str) -> float:
        return sum(
            p.get("entry_price", 0.0) * p.get("qty", 0)
            for p in self.open_positions.values()
            if p.get("sector", "").upper() == sector.upper()
        )

    def get_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "trade_date":           self._today,
                "daily_realized_pnl":   round(self.daily_realized_pnl, 2),
                "orders_today":         self.orders_today,
                "consecutive_losses":   self.consecutive_losses,
                "open_trade_count":     self.open_trade_count,
                "total_open_exposure":  round(self.total_open_exposure, 2),
                "kill_switch":          self.kill_switch,
                "auto_trading":         self.auto_trading,
                "open_positions":       dict(self.open_positions),
            }


# ─────────────────────────────────────────────────────────────────────────────
# Position Sizing Methods
# ─────────────────────────────────────────────────────────────────────────────

class PositionSizer:
    """Computes recommended order quantity using one of five methods."""

    def __init__(self, config: RiskConfig):
        self.config = config

    def compute(
        self,
        request: OrderRiskRequest,
        available_margin: float,
    ) -> Dict[str, Any]:
        m = request.sizing_method

        if m == SizingMethod.FIXED_QUANTITY:
            return self._fixed_quantity(request)
        elif m == SizingMethod.FIXED_CAPITAL:
            return self._fixed_capital(request, available_margin)
        elif m == SizingMethod.RISK_PCT:
            return self._risk_pct(request)
        elif m == SizingMethod.ATR_BASED:
            return self._atr_based(request)
        elif m == SizingMethod.MAX_EXPOSURE:
            return self._max_exposure(request, available_margin)
        else:
            return self._fixed_quantity(request)

    def _fixed_quantity(self, req: OrderRiskRequest) -> Dict:
        qty = req.quantity
        trade_val = qty * req.price
        margin = trade_val * (self.config.get("intraday_margin_pct") / 100.0
                              if req.product == "I"
                              else self.config.get("delivery_margin_pct") / 100.0)
        return {"method": "FIXED_QUANTITY", "quantity": qty,
                "trade_value": round(trade_val, 2), "margin_required": round(margin, 2)}

    def _fixed_capital(self, req: OrderRiskRequest, available: float) -> Dict:
        capital_to_deploy = min(self.config.capital * 0.10, available)  # max 10% per trade
        qty = max(1, int(capital_to_deploy / max(req.price, 1)))
        trade_val = qty * req.price
        margin_pct = (self.config.get("intraday_margin_pct") / 100.0
                      if req.product == "I"
                      else self.config.get("delivery_margin_pct") / 100.0)
        margin = trade_val * margin_pct
        return {"method": "FIXED_CAPITAL", "quantity": qty,
                "trade_value": round(trade_val, 2), "margin_required": round(margin, 2)}

    def _risk_pct(self, req: OrderRiskRequest) -> Dict:
        risk_amount = self.config.capital * (self.config.risk_pct / 100.0)
        risk_per_share = abs(req.price - req.stop_loss) if req.stop_loss > 0 else req.price * 0.02
        qty = max(1, int(risk_amount / max(risk_per_share, 0.01)))
        trade_val = qty * req.price
        margin_pct = (self.config.get("intraday_margin_pct") / 100.0
                      if req.product == "I"
                      else self.config.get("delivery_margin_pct") / 100.0)
        margin = trade_val * margin_pct
        return {"method": "RISK_PCT", "quantity": qty,
                "risk_per_share": round(risk_per_share, 2),
                "risk_amount": round(risk_amount, 2),
                "trade_value": round(trade_val, 2), "margin_required": round(margin, 2)}

    def _atr_based(self, req: OrderRiskRequest) -> Dict:
        atr = req.atr if req.atr > 0 else req.price * 0.015
        risk_amount = self.config.capital * (self.config.risk_pct / 100.0)
        qty = max(1, int(risk_amount / (atr * 2)))  # 2× ATR as risk distance
        trade_val = qty * req.price
        margin_pct = (self.config.get("intraday_margin_pct") / 100.0
                      if req.product == "I"
                      else self.config.get("delivery_margin_pct") / 100.0)
        margin = trade_val * margin_pct
        return {"method": "ATR_BASED", "quantity": qty, "atr": round(atr, 2),
                "trade_value": round(trade_val, 2), "margin_required": round(margin, 2)}

    def _max_exposure(self, req: OrderRiskRequest, available: float) -> Dict:
        max_pos_pct = self.config.get("max_position_size_pct") / 100.0
        cap_limit = self.config.capital * max_pos_pct
        margin_pct = (self.config.get("intraday_margin_pct") / 100.0
                      if req.product == "I"
                      else self.config.get("delivery_margin_pct") / 100.0)
        max_by_margin = available / max(margin_pct, 0.01) if margin_pct > 0 else 0
        capital_budget = min(cap_limit, max_by_margin)
        qty = max(1, int(capital_budget / max(req.price, 1)))
        trade_val = qty * req.price
        margin = trade_val * margin_pct
        return {"method": "MAX_EXPOSURE", "quantity": qty,
                "trade_value": round(trade_val, 2), "margin_required": round(margin, 2)}


# ─────────────────────────────────────────────────────────────────────────────
# Main Risk Engine — validates every order before execution
# ─────────────────────────────────────────────────────────────────────────────

class LiveRiskEngine:
    """
    Sprint M6: Production Risk Engine.
    Call `validate_order()` before every live Paytm order placement.
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> "LiveRiskEngine":
        if cls._instance is None:
            cls._instance = LiveRiskEngine()
        return cls._instance

    def __init__(self, config_path: str = "config.json"):
        self.config = RiskConfig(config_path)
        self.tracker = DailyRiskTracker.get_instance()
        self.sizer = PositionSizer(self.config)
        self.logger = logging.getLogger(self.__class__.__name__)

    # ── Main Validation Gate ─────────────────────────────────────────────────

    def validate_order(self, request: OrderRiskRequest) -> RiskCheckResult:
        """
        Full pre-trade risk check. Returns RiskCheckResult.
        If decision is REJECTED, the Order Engine MUST NOT place the order.
        """
        reasons: List[str] = []
        warnings: List[str] = []

        # Guard: Invalid order price or quantity
        if request.quantity <= 0 or request.price <= 0:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                approved_quantity=0,
                reasons=["Invalid order parameters: quantity and price must be greater than zero."],
            )

        # Task 5: Kill Switch — hard stop
        if self.tracker.kill_switch:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                approved_quantity=0,
                reasons=["🔴 KILL SWITCH ACTIVE — All live trading halted."],
            )

        if not self.tracker.auto_trading and request.action.upper() == "BUY":
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                approved_quantity=0,
                reasons=["Auto trading is disabled. Only manual orders allowed after explicit re-enable."],
            )

        # Task 4: Duplicate order protection
        if self.tracker.is_duplicate(request.symbol, request.action, request.quantity, request.price):
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                approved_quantity=0,
                reasons=[f"Duplicate order detected: {request.symbol} {request.action} {request.quantity}@{request.price}. "
                          "Previous order still pending."],
            )

        # Already have an open BUY position for the same symbol?
        if request.action.upper() == "BUY" and request.symbol in self.tracker.open_positions:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                approved_quantity=0,
                reasons=[f"Repeated BUY blocked: Already have an open long position in {request.symbol}."],
            )

        # Task 2: Daily loss limit
        snap = self.tracker.get_snapshot()
        if snap["daily_realized_pnl"] <= -self.config.daily_loss_limit:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                approved_quantity=0,
                reasons=[f"Daily Loss Limit hit (₹{abs(snap['daily_realized_pnl']):,.0f} / ₹{self.config.daily_loss_limit:,.0f}). "
                          "Trading halted for the day."],
            )

        # Task 2: Daily profit target reached — warn but don't block
        if snap["daily_realized_pnl"] >= self.config.daily_profit_target:
            warnings.append(f"Daily Profit Target reached (₹{snap['daily_realized_pnl']:,.0f}). Consider stopping for the day.")

        # Task 2: Max consecutive losses
        if snap["consecutive_losses"] >= self.config.max_consecutive_losses:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                approved_quantity=0,
                reasons=[f"Max Consecutive Losses reached ({snap['consecutive_losses']}). "
                          "Please review strategy before continuing."],
            )

        # Task 2: Max open trades
        if request.action.upper() == "BUY" and snap["open_trade_count"] >= self.config.max_open_trades:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                approved_quantity=0,
                reasons=[f"Max Open Trades limit reached ({snap['open_trade_count']} / {self.config.max_open_trades})."],
            )

        # Task 2: Max orders per day
        if snap["orders_today"] >= self.config.max_orders_per_day:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                approved_quantity=0,
                reasons=[f"Max Orders Per Day limit reached ({snap['orders_today']} / {self.config.max_orders_per_day})."],
            )

        # Task 1: Position sizing — compute approved qty
        # Try to get live margin from broker; fall back to config capital
        available_margin = self._get_available_margin()
        size_data = self.sizer.compute(request, available_margin)
        computed_qty = size_data.get("quantity", request.quantity)
        margin_req = size_data.get("margin_required", 0.0)
        trade_val = size_data.get("trade_value", request.price * request.quantity)

        # Task 3: Available margin check
        if margin_req > available_margin:
            reduced_qty = max(0, int(available_margin / max(request.price * (
                self.config.get("intraday_margin_pct") / 100.0
                if request.product == "I"
                else self.config.get("delivery_margin_pct") / 100.0
            ), 1)))
            if reduced_qty < 1:
                return RiskCheckResult(
                    decision=RiskDecision.REJECTED,
                    approved_quantity=0,
                    reasons=[f"Insufficient Margin: Required ₹{margin_req:,.0f}, Available ₹{available_margin:,.0f}."],
                    position_size_data=size_data,
                )
            warnings.append(
                f"Margin reduced from {computed_qty} to {reduced_qty} shares "
                f"due to margin constraint (Available ₹{available_margin:,.0f})."
            )
            computed_qty = reduced_qty
            trade_val = computed_qty * request.price
            margin_req = trade_val * (self.config.get("intraday_margin_pct") / 100.0
                                      if request.product == "I"
                                      else self.config.get("delivery_margin_pct") / 100.0)

        # Task 3: Total portfolio exposure check
        new_total_exposure = snap["total_open_exposure"] + trade_val
        exposure_limit = self.config.capital * (self.config.total_exposure_limit_pct / 100.0)
        if new_total_exposure > exposure_limit:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                approved_quantity=0,
                reasons=[f"Total Exposure Limit breached: ₹{new_total_exposure:,.0f} > ₹{exposure_limit:,.0f} "
                          f"({self.config.total_exposure_limit_pct:.0f}% of capital)."],
                position_size_data=size_data,
            )

        # Task 3: Sector exposure check
        sector_exp = self.tracker.sector_exposure(request.sector) + trade_val
        sector_limit = self.config.capital * (self.config.sector_exposure_limit_pct / 100.0)
        if sector_exp > sector_limit:
            reasons.append(
                f"Sector '{request.sector}' Exposure Limit breached: "
                f"₹{sector_exp:,.0f} > ₹{sector_limit:,.0f}."
            )

        if reasons:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                approved_quantity=0,
                reasons=reasons,
                warnings=warnings,
                position_size_data=size_data,
            )

        # Decision
        final_qty = min(computed_qty, request.quantity)
        decision = (RiskDecision.REDUCED if final_qty < request.quantity
                    else RiskDecision.APPROVED)

        if final_qty < request.quantity:
            warnings.append(
                f"Quantity reduced from {request.quantity} to {final_qty} "
                f"based on {request.sizing_method} sizing."
            )

        risk_report = self._build_risk_report(snap, available_margin, margin_req, trade_val, final_qty, request)

        self.logger.info(
            f"RiskEngine [{decision}] {request.symbol} {request.action} "
            f"qty={final_qty} margin=₹{margin_req:,.0f}"
        )
        return RiskCheckResult(
            decision=decision,
            approved_quantity=final_qty,
            reasons=reasons,
            warnings=warnings,
            position_size_data=size_data,
            risk_report=risk_report,
        )

    # ── Task 5: Kill Switch Controls ─────────────────────────────────────────

    def activate_kill_switch(self):
        """Emergency: stop all trading immediately."""
        self.tracker.activate_kill_switch()

    def deactivate_kill_switch(self):
        self.tracker.deactivate_kill_switch()

    def disable_auto_trading(self):
        self.tracker.disable_auto_trading()

    def enable_auto_trading(self):
        self.tracker.enable_auto_trading()

    def cancel_all_pending(self) -> Dict[str, Any]:
        """Cancels all pending order locks (clears dedup set)."""
        count = len(self.tracker.pending_order_keys)
        self.tracker.pending_order_keys.clear()
        self.logger.warning(f"Cancelled {count} pending order locks via Kill Switch.")
        return {"cancelled_locks": count}

    # ── Task 6: Risk Report ──────────────────────────────────────────────────

    def get_risk_report(self) -> Dict[str, Any]:
        """Full risk dashboard snapshot for Task 6."""
        snap = self.tracker.get_snapshot()
        available_margin = self._get_available_margin()
        capital = self.config.capital

        daily_loss_used = abs(min(0.0, snap["daily_realized_pnl"]))
        daily_loss_remaining = max(0.0, self.config.daily_loss_limit - daily_loss_used)
        risk_used_pct = round((daily_loss_used / max(self.config.daily_loss_limit, 1)) * 100, 1)
        risk_remaining_pct = round(100.0 - risk_used_pct, 1)
        exposure_pct = round((snap["total_open_exposure"] / max(capital, 1)) * 100, 1)
        buying_power = max(0.0, available_margin)

        return {
            # Task 6 required fields
            "risk_used":           round(daily_loss_used, 2),
            "risk_remaining":      round(daily_loss_remaining, 2),
            "risk_used_pct":       risk_used_pct,
            "risk_remaining_pct":  risk_remaining_pct,
            "available_margin":    round(available_margin, 2),
            "buying_power":        round(buying_power, 2),
            "daily_loss":          round(snap["daily_realized_pnl"], 2),
            "daily_profit":        round(max(0.0, snap["daily_realized_pnl"]), 2),
            # Supplementary
            "daily_profit_target": self.config.daily_profit_target,
            "daily_loss_limit":    self.config.daily_loss_limit,
            "capital":             capital,
            "total_exposure":      round(snap["total_open_exposure"], 2),
            "exposure_pct":        exposure_pct,
            "open_trades":         snap["open_trade_count"],
            "max_open_trades":     self.config.max_open_trades,
            "orders_today":        snap["orders_today"],
            "max_orders_per_day":  self.config.max_orders_per_day,
            "consecutive_losses":  snap["consecutive_losses"],
            "max_consecutive_losses": self.config.max_consecutive_losses,
            "kill_switch":         snap["kill_switch"],
            "auto_trading":        snap["auto_trading"],
        }

    # ── Internal Helpers ─────────────────────────────────────────────────────

    def _get_available_margin(self) -> float:
        """Try live Paytm broker funds; fall back to config capital."""
        try:
            from broker.paytm.paytm_broker import PaytmBroker
            broker = PaytmBroker()
            if broker.is_connected:
                funds = broker.get_funds()
                return float(funds.available_margin)
        except Exception:
            pass
        return float(self.config.capital) * 0.85  # conservative fallback (85% of config capital)

    def _build_risk_report(
        self,
        snap: Dict,
        available_margin: float,
        margin_req: float,
        trade_val: float,
        qty: int,
        request: OrderRiskRequest,
    ) -> Dict:
        return {
            "symbol":             request.symbol,
            "action":             request.action,
            "approved_quantity":  qty,
            "margin_required":    round(margin_req, 2),
            "available_margin":   round(available_margin, 2),
            "trade_value":        round(trade_val, 2),
            "daily_pnl":          round(snap["daily_realized_pnl"], 2),
            "orders_today":       snap["orders_today"],
            "open_trades":        snap["open_trade_count"],
            "total_exposure":     round(snap["total_open_exposure"], 2),
            "consecutive_losses": snap["consecutive_losses"],
        }
