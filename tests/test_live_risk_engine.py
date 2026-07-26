"""
Sprint M6 — Risk Engine Unit Tests
===================================
Tests for core/live_risk_engine.py
"""

import pytest
import os
import tempfile
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ─────────────────────────────────────────────────────────────────────────────
# Helpers / Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_config(tmp_path):
    """Write a minimal config.json and return path."""
    import json
    cfg = {
        "capital": 1000000.0,
        "risk_pct": 1.0,
        "daily_loss_limit": 5000.0,
        "daily_profit_target": 15000.0,
        "max_consecutive_losses": 3,
        "max_open_trades": 5,
        "max_orders_per_day": 20,
        "total_exposure_limit_pct": 80.0,
        "sector_exposure_limit_pct": 30.0,
        "intraday_margin_pct": 20.0,
        "delivery_margin_pct": 100.0,
        "max_position_size_pct": 10.0,
        "kill_switch_active": False,
        "auto_trading_enabled": True,
    }
    p = tmp_path / "config.json"
    p.write_text(json.dumps(cfg))
    return str(p)


@pytest.fixture
def tracker(tmp_path):
    """Fresh DailyRiskTracker backed by a temp DB."""
    from core.live_risk_engine import DailyRiskTracker
    DailyRiskTracker._instance = None  # reset singleton
    t = DailyRiskTracker(db_path=str(tmp_path / "risk.db"))
    yield t
    DailyRiskTracker._instance = None


@pytest.fixture
def engine(tmp_config, tmp_path, monkeypatch):
    """LiveRiskEngine wired to a fresh tracker and config, broker fallback disabled."""
    from core.live_risk_engine import LiveRiskEngine, DailyRiskTracker
    LiveRiskEngine._instance = None
    DailyRiskTracker._instance = None

    eng = LiveRiskEngine(config_path=tmp_config)
    # Override tracker to use temp DB
    eng.tracker = DailyRiskTracker(db_path=str(tmp_path / "risk.db"))
    yield eng

    LiveRiskEngine._instance = None
    DailyRiskTracker._instance = None


def make_req(symbol="RELIANCE", action="BUY", qty=10, price=2500.0, **kwargs):
    from core.live_risk_engine import OrderRiskRequest, SizingMethod
    return OrderRiskRequest(
        symbol=symbol,
        action=action,
        quantity=qty,
        price=price,
        stop_loss=kwargs.get("stop_loss", 2450.0),
        atr=kwargs.get("atr", 0.0),
        sector=kwargs.get("sector", "ENERGY"),
        product=kwargs.get("product", "I"),
        order_type=kwargs.get("order_type", "MARKET"),
        sizing_method=kwargs.get("sizing_method", SizingMethod.FIXED_QUANTITY),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Task 1 — Position Sizing
# ─────────────────────────────────────────────────────────────────────────────

class TestPositionSizing:
    def test_fixed_quantity_passthrough(self, engine):
        """FIXED_QUANTITY should use the submitted qty unchanged."""
        from core.live_risk_engine import SizingMethod
        req = make_req(qty=5, sizing_method=SizingMethod.FIXED_QUANTITY)
        result = engine.validate_order(req)
        assert result.is_approved
        assert result.approved_quantity == 5

    def test_risk_pct_sizing_reduces_large_qty(self, engine):
        """With 1% risk on ₹10L capital and SL ₹5/share at ₹100 price, max qty ≈ 2000.
        Trade value ≈ 2000×₹100 = ₹2L → well within sector/total limits."""
        from core.live_risk_engine import SizingMethod
        req = make_req(qty=50000, price=100, stop_loss=95,
                       sector="GENERAL",
                       sizing_method=SizingMethod.RISK_PCT)
        result = engine.validate_order(req)
        # RISK_PCT caps to ≈2000 shares (₹10K risk / ₹5 SL distance)
        assert result.is_approved
        assert result.approved_quantity < 50000

    def test_atr_based_uses_atr(self, engine):
        from core.live_risk_engine import SizingMethod
        req = make_req(qty=1000, price=500, atr=15.0,
                       sizing_method=SizingMethod.ATR_BASED)
        result = engine.validate_order(req)
        assert result.is_approved
        assert result.approved_quantity <= 1000

    def test_fixed_capital_bounded_by_10pct(self, engine):
        from core.live_risk_engine import SizingMethod
        req = make_req(qty=10000, price=200, sizing_method=SizingMethod.FIXED_CAPITAL)
        result = engine.validate_order(req)
        # Max 10% of ₹10L = ₹1L → at ₹200/share max = 500 shares
        assert result.is_approved
        assert result.approved_quantity <= 500

    def test_max_exposure_capped(self, engine):
        from core.live_risk_engine import SizingMethod
        req = make_req(qty=99999, price=1000, sizing_method=SizingMethod.MAX_EXPOSURE)
        result = engine.validate_order(req)
        assert result.is_approved
        assert result.approved_quantity < 99999


# ─────────────────────────────────────────────────────────────────────────────
# Task 2 — Daily Protection
# ─────────────────────────────────────────────────────────────────────────────

class TestDailyProtection:
    def test_blocks_when_daily_loss_limit_hit(self, engine):
        engine.tracker.daily_realized_pnl = -5001.0
        result = engine.validate_order(make_req())
        assert result.decision == "REJECTED"
        assert any("Daily Loss Limit" in r for r in result.reasons)

    def test_passes_before_loss_limit(self, engine):
        engine.tracker.daily_realized_pnl = -2000.0
        result = engine.validate_order(make_req())
        assert result.is_approved

    def test_warns_on_profit_target_reached(self, engine):
        engine.tracker.daily_realized_pnl = 16000.0
        result = engine.validate_order(make_req())
        assert result.is_approved
        assert any("Profit Target" in w for w in result.warnings)

    def test_blocks_max_consecutive_losses(self, engine):
        engine.tracker.consecutive_losses = 3
        result = engine.validate_order(make_req())
        assert result.decision == "REJECTED"
        assert any("Consecutive" in r for r in result.reasons)

    def test_passes_under_consecutive_losses(self, engine):
        engine.tracker.consecutive_losses = 2
        result = engine.validate_order(make_req())
        assert result.is_approved

    def test_blocks_max_open_trades(self, engine):
        for i in range(5):
            engine.tracker.open_positions[f"STOCK{i}"] = {
                "qty": 1, "entry_price": 100, "stop_loss": 90, "sector": "IT", "product": "I"
            }
        result = engine.validate_order(make_req(symbol="NEWSTOCK"))
        assert result.decision == "REJECTED"
        assert any("Max Open Trades" in r for r in result.reasons)

    def test_blocks_max_orders_per_day(self, engine):
        engine.tracker.orders_today = 20
        result = engine.validate_order(make_req())
        assert result.decision == "REJECTED"
        assert any("Max Orders" in r for r in result.reasons)


# ─────────────────────────────────────────────────────────────────────────────
# Task 3 — Exposure Control
# ─────────────────────────────────────────────────────────────────────────────

class TestExposureControl:
    def test_rejects_beyond_total_exposure(self, engine):
        # Fill up 75% of ₹10L = ₹7.5L exposure
        engine.tracker.open_positions["EXISTING"] = {
            "qty": 750, "entry_price": 1000, "stop_loss": 950, "sector": "BANK", "product": "I"
        }
        # New order of ₹1L → total ₹8.5L > ₹8L limit (80%)
        req = make_req(qty=100, price=1000)
        result = engine.validate_order(req)
        assert result.decision == "REJECTED"
        assert any("Total Exposure" in r for r in result.reasons)

    def test_rejects_beyond_sector_exposure(self, engine):
        # Fill ENERGY sector with ₹2.5L (25%) already
        engine.tracker.open_positions["ONGC"] = {
            "qty": 500, "entry_price": 500, "stop_loss": 480, "sector": "ENERGY", "product": "I"
        }
        # New ENERGY trade adding ₹1L → sector total ₹3.5L > ₹3L limit (30%)
        req = make_req(symbol="BPCL", qty=200, price=500, sector="ENERGY")
        result = engine.validate_order(req)
        assert result.decision == "REJECTED"
        assert any("sector" in r.lower() or "Sector" in r for r in result.reasons)


# ─────────────────────────────────────────────────────────────────────────────
# Task 4 — Duplicate Protection
# ─────────────────────────────────────────────────────────────────────────────

class TestDuplicateProtection:
    def test_duplicate_order_rejected(self, engine):
        req = make_req(symbol="TCS", action="BUY", qty=10, price=3500.0)
        # Lock the key manually
        engine.tracker.lock_order("TCS", "BUY", 10, 3500.0)
        result = engine.validate_order(req)
        assert result.decision == "REJECTED"
        assert any("Duplicate" in r for r in result.reasons)

    def test_repeated_buy_same_symbol_rejected(self, engine):
        # Already have open long in TCS
        engine.tracker.open_positions["TCS"] = {
            "qty": 5, "entry_price": 3500, "stop_loss": 3400, "sector": "IT", "product": "I"
        }
        req = make_req(symbol="TCS", action="BUY", qty=5, price=3510.0)
        result = engine.validate_order(req)
        assert result.decision == "REJECTED"
        assert any("Repeated BUY" in r for r in result.reasons)

    def test_different_symbol_allowed(self, engine):
        engine.tracker.open_positions["TCS"] = {
            "qty": 5, "entry_price": 3500, "stop_loss": 3400, "sector": "IT", "product": "I"
        }
        req = make_req(symbol="INFY", action="BUY", qty=5, price=1500.0)
        result = engine.validate_order(req)
        assert result.is_approved

    def test_lock_released_allows_resubmit(self, engine):
        req = make_req(symbol="WIPRO", action="BUY", qty=10, price=400.0)
        key = engine.tracker.lock_order("WIPRO", "BUY", 10, 400.0)
        # Release the lock
        engine.tracker.release_order_lock(key)
        result = engine.validate_order(req)
        assert result.is_approved


# ─────────────────────────────────────────────────────────────────────────────
# Task 5 — Kill Switch
# ─────────────────────────────────────────────────────────────────────────────

class TestKillSwitch:
    def test_kill_switch_blocks_all(self, engine):
        engine.activate_kill_switch()
        result = engine.validate_order(make_req())
        assert result.decision == "REJECTED"
        assert any("KILL SWITCH" in r for r in result.reasons)

    def test_deactivate_allows_trading(self, engine):
        engine.activate_kill_switch()
        engine.deactivate_kill_switch()
        result = engine.validate_order(make_req())
        assert result.is_approved

    def test_disable_auto_trading_blocks_buy(self, engine):
        engine.disable_auto_trading()
        result = engine.validate_order(make_req(action="BUY"))
        assert result.decision == "REJECTED"

    def test_enable_auto_trading_allows_buy(self, engine):
        engine.disable_auto_trading()
        engine.enable_auto_trading()
        result = engine.validate_order(make_req(action="BUY"))
        assert result.is_approved

    def test_cancel_all_pending_clears_locks(self, engine):
        engine.tracker.lock_order("A", "BUY", 5, 100.0)
        engine.tracker.lock_order("B", "SELL", 5, 200.0)
        assert len(engine.tracker.pending_order_keys) == 2
        cancelled = engine.cancel_all_pending()
        assert cancelled["cancelled_locks"] == 2
        assert len(engine.tracker.pending_order_keys) == 0


# ─────────────────────────────────────────────────────────────────────────────
# Task 6 — Risk Report
# ─────────────────────────────────────────────────────────────────────────────

class TestRiskReport:
    def test_report_has_required_fields(self, engine):
        report = engine.get_risk_report()
        required = [
            "risk_used", "risk_remaining", "available_margin", "buying_power",
            "daily_loss", "daily_profit", "risk_used_pct", "risk_remaining_pct",
        ]
        for key in required:
            assert key in report, f"Missing field: {key}"

    def test_risk_remaining_decreases_with_losses(self, engine):
        engine.tracker.daily_realized_pnl = -2000.0
        report = engine.get_risk_report()
        assert report["risk_used"] == pytest.approx(2000.0)
        assert report["risk_remaining"] == pytest.approx(3000.0)

    def test_kill_switch_reflected_in_report(self, engine):
        engine.activate_kill_switch()
        report = engine.get_risk_report()
        assert report["kill_switch"] is True

    def test_auto_trading_reflected_in_report(self, engine):
        engine.disable_auto_trading()
        report = engine.get_risk_report()
        assert report["auto_trading"] is False


# ─────────────────────────────────────────────────────────────────────────────
# DailyRiskTracker persistence
# ─────────────────────────────────────────────────────────────────────────────

class TestDailyRiskTracker:
    def test_register_buy_adds_open_position(self, tracker):
        tracker.register_order_executed("SBIN", "BUY", 100, 550.0, sl=530.0, sector="BANK")
        assert "SBIN" in tracker.open_positions
        assert tracker.open_positions["SBIN"]["qty"] == 100

    def test_register_sell_removes_position_and_tracks_pnl(self, tracker):
        tracker.register_order_executed("SBIN", "BUY", 100, 550.0)
        tracker.register_order_executed("SBIN", "SELL", 100, 570.0)
        assert "SBIN" not in tracker.open_positions
        assert tracker.daily_realized_pnl == pytest.approx(2000.0)

    def test_consecutive_losses_incremented_on_loss(self, tracker):
        tracker.register_order_executed("HDFC", "BUY", 50, 1600.0)
        tracker.register_order_executed("HDFC", "SELL", 50, 1550.0)  # -₹2500 loss
        assert tracker.consecutive_losses == 1

    def test_consecutive_losses_reset_on_win(self, tracker):
        tracker.consecutive_losses = 2
        tracker.register_order_executed("HDFC", "BUY", 50, 1600.0)
        tracker.register_order_executed("HDFC", "SELL", 50, 1700.0)  # profit
        assert tracker.consecutive_losses == 0

    def test_sector_exposure_calculated_correctly(self, tracker):
        tracker.open_positions["SBIN"] = {"qty": 100, "entry_price": 550, "sector": "BANK", "product": "I", "stop_loss": 530}
        tracker.open_positions["HDFC"] = {"qty": 50, "entry_price": 1600, "sector": "BANK", "product": "I", "stop_loss": 1550}
        exp = tracker.sector_exposure("BANK")
        assert exp == pytest.approx(55000 + 80000)  # 100*550 + 50*1600

    def test_snapshot_complete(self, tracker):
        snap = tracker.get_snapshot()
        expected = ["trade_date", "daily_realized_pnl", "orders_today", "consecutive_losses",
                    "open_trade_count", "total_open_exposure", "kill_switch", "auto_trading"]
        for k in expected:
            assert k in snap
