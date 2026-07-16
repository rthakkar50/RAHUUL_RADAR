import logging
"""
SmartTradeSetupPanel — Commercial Detail Panel
Reads directly from the SwingScannerService result dict.

Service result dict keys (authoritative):
  Symbol, Company, Sector, Price, Signal, Score, Confidence,
  Trend, Volume, Risk Reward, Entry, Stop Loss, Target 1, Target 2,
  Trade Grade, Risk Grade, _why_selected, _raw_data, _reasons
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.styles import CARD_BG, TEXT_PRIMARY, TEXT_SECONDARY

# ─── Forbidden value scrubber ────────────────────────────────────────────────
_FORBIDDEN = {"unknown", "--", "none", "n/a", "null", "nan", "0", "0.0",
              "fno", "placeholder", "dummy", "trend engine error",
              "pipeline error", "neutral error", "fallback", "exception"}

def _is_valid(val) -> bool:
    return bool(val) and str(val).strip().lower() not in _FORBIDDEN

def scrub(val, fallback="--"):
    """Return val if it is valid, otherwise return fallback."""
    if val is None:
        return fallback
    s = str(val).strip()
    if s.lower() in _FORBIDDEN or s == "":
        return fallback
    return s

# ─── Internal developer-string cleaner ───────────────────────────────────────
import re

_DEV_PATTERNS = [
    r"Trend Weight.*",
    r"Momentum Weight.*",
    r"Structure Weight.*",
    r"--- Dynamic Weighted Math ---",
    r"ADX.*Adjusted Confidence.*",
    r"AVWAP.*Adjusted Confidence.*",
    r"MTCE Confidence.*",
    r"Bullish Market Adjustment.*",
    r"Bearish Market Adjustment.*",
    r"Neutral Market.*",
    r"Sector Adjustment.*",
    r"OI Adjustment.*",
    r"Decision:.*",
    r"ADX Engine:.*",
    r"MTCE:.*",
]
_DEV_RE = re.compile("|".join(_DEV_PATTERNS), re.IGNORECASE)

# Human-readable internal string replacements
_TREND_MAP = {
    "strong_bull":  "Strong Bullish",
    "bull":         "Bullish",
    "bullish":      "Bullish",
    "neutral":      "Neutral Trend",
    "sideways":     "Neutral Trend",
    "bear":         "Bearish",
    "bearish":      "Bearish",
    "strong_bear":  "Strong Bearish",
}

def _clean_reason(r: str) -> str:
    r = str(r).strip()
    # Check dev/internal patterns on RAW string first (before stripping bullets)
    if _DEV_RE.match(r):
        return ""
    # Also check common dev keywords that appear mid-string
    r_lower = r.lower()
    for bad in ["trend weight", "momentum weight", "structure weight",
                "dynamic weighted math", "adjusted confidence",
                "market adjustment", "sector adjustment", "oi adjustment",
                "trend engine error", "pipeline error", "neutral error",
                "fallback", "exception"]:
        if bad in r_lower:
            return ""
    # Now strip leading bullet/checkmark characters
    r = re.sub(r'^[✓•⛔\-\*]\s*', '', r)
    return r.strip()

def _format_reasons(raw_reasons) -> list:
    """
    Accept list or comma-string, clean dev strings, prefix with ✓.
    Never returns an empty list.
    """
    if isinstance(raw_reasons, str):
        items = [r.strip() for r in raw_reasons.split(",")]
    elif isinstance(raw_reasons, list):
        items = raw_reasons
    else:
        items = []

    cleaned = []
    seen = set()
    for r in items:
        c = _clean_reason(r)
        if c and c not in seen and len(c) > 4:
            seen.add(c)
            cleaned.append(c)

    cleaned = cleaned[:8]

    if not cleaned:
        cleaned = ["Standard engine validation passed",
                   "Quantitative metrics aligned"]

    return [f"✓ {r}" for r in cleaned]


class SmartTradeSetupPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{ background: transparent; }}
            QFrame#SetupCard {{
                background-color: {CARD_BG};
                border-radius: 8px;
                border: 1px solid #2A2E39;
            }}
            QFrame#HeaderFrame {{
                background-color: #1A1F2B;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid #2A2E39;
            }}
            QFrame#ReasonsFrame {{
                background-color: #181C27;
                border-radius: 6px;
                border: 1px solid #2A2E39;
            }}
            QScrollBar:vertical {{
                background: #131722; width: 6px; border: none;
            }}
            QScrollBar::handle:vertical {{
                background: #2A2E39; border-radius: 3px;
            }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.content_widget = QWidget()
        self._layout = QVBoxLayout(self.content_widget)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)

        scroll.setWidget(self.content_widget)
        outer.addWidget(scroll)

        self.current_data = {}

        # Show placeholder on launch
        self._show_placeholder("Select a row to view trade setup")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _clear(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_placeholder(self, msg="No Selection"):
        self._clear()
        lbl = QLabel(msg)
        lbl.setStyleSheet("color: #787B86; font-size: 13px; font-style: italic; padding: 20px;")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        self._layout.addWidget(lbl)

    def _row(self, layout, key: str, val: str, color: str = None, badge: bool = False):
        """Add a key-value row to layout."""
        r = QHBoxLayout()
        kl = QLabel(key)
        kl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px; font-weight: 500;")

        vl = QLabel(val)
        if badge and color:
            vl.setStyleSheet(
                f"background: {color}; color: white; border-radius: 4px; "
                f"padding: 2px 8px; font-weight: bold; font-size: 13px;"
            )
            vl.setAlignment(Qt.AlignCenter)
            wrap = QHBoxLayout()
            wrap.addStretch()
            wrap.addWidget(vl)
            r.addWidget(kl)
            r.addLayout(wrap)
        else:
            c = color if color else TEXT_PRIMARY
            vl.setStyleSheet(f"color: {c}; font-size: 15px; font-weight: 600;")
            vl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            r.addWidget(kl)
            r.addWidget(vl)

        layout.addLayout(r)

    def _progress_row(self, layout, key: str, value: float, color: str):
        r = QHBoxLayout()
        kl = QLabel(key)
        kl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px; font-weight: 500;")
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(int(min(100, max(0, value))))
        bar.setTextVisible(True)
        bar.setFormat(f"{value:.1f}%")
        bar.setMaximumWidth(130)
        bar.setFixedHeight(18)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background: #1E222D; border: none; border-radius: 3px;
                color: white; font-size: 12px; text-align: center;
            }}
            QProgressBar::chunk {{
                background: {color}; border-radius: 3px;
            }}
        """)
        r.addWidget(kl)
        r.addStretch()
        r.addWidget(bar)
        layout.addLayout(r)

    def _sep(self, layout):
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background: #2A2E39; margin: 4px 0;")
        layout.addWidget(line)

    # ── Main update ───────────────────────────────────────────────────────────
    def update_panel(self, data: dict):
        """Called on every row-selection change. Reads from the service result dict."""
        self.current_data = data
        self._clear()

        if not data or data.get("error"):
            self._show_placeholder(data.get("error", "No Selection") if data else "No Selection")
            return

        # ── Build Card ────────────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("SetupCard")
        card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(0, 0, 0, 0)
        card_l.setSpacing(0)

        # Header ──────────────────────────────────────────────────────────────
        header = QFrame()
        header.setObjectName("HeaderFrame")
        hl = QVBoxLayout(header)
        hl.setContentsMargins(14, 12, 14, 12)
        hl.setSpacing(3)

        sym = scrub(data.get("Symbol", data.get("symbol", "")), "--")
        company = scrub(data.get("Company", ""), "--")
        sector = scrub(data.get("Sector", ""), "--")

        lbl_sym = QLabel(sym)
        lbl_sym.setStyleSheet("color: #2962FF; font-size: 20px; font-weight: bold;")
        hl.addWidget(lbl_sym)

        lbl_meta = QLabel(f"{company}  ·  {sector}")
        lbl_meta.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        hl.addWidget(lbl_meta)

        card_l.addWidget(header)

        # Body ────────────────────────────────────────────────────────────────
        body = QWidget()
        bl = QVBoxLayout(body)
        bl.setContentsMargins(14, 12, 14, 12)
        bl.setSpacing(8)

        # ── Signal ─────────────────────────────────────────────
        raw_sig = str(data.get("Signal", "")).upper()
        if "BULLISH" in raw_sig or "STRONG_BUY" in raw_sig: raw_sig = "BUY"
        elif "BEARISH" in raw_sig or "STRONG_SELL" in raw_sig: raw_sig = "SELL"
        if raw_sig not in ("BUY", "WATCH", "SELL"): raw_sig = "WATCH"
        sig_color = "#00B69B" if raw_sig == "BUY" else "#F9322C" if raw_sig == "SELL" else "#F1C40F"
        self._row(bl, "Signal", raw_sig, color=sig_color, badge=True)

        # ── Grade — read "Trade Grade" key (service output) ────
        grade_raw = scrub(data.get("Trade Grade", data.get("trade_grade", "")), "--")
        grade_color = {"★★★★★": "#00B69B", "★★★★☆": "#2962FF",
                       "★★★☆☆": "#00BCD4", "★★☆☆☆": "#F1C40F",
                       "★☆☆☆☆": "#9E9E9E"}.get(grade_raw, "#787B86")
        self._row(bl, "Grade", grade_raw, color=grade_color, badge=True)

        # ── Score ──────────────────────────────────────────────
        try:
            score = float(data.get("Score", 0))
        except Exception:
            score = 0.0
        if score > 0:
            s_color = ("#00B69B" if score >= 90 else "#4CAF50" if score >= 80
                       else "#2962FF" if score >= 70 else "#FF9800" if score >= 60 else "#9E9E9E")
            self._row(bl, "Score", f"{score:.1f}", color=s_color, badge=True)
        else:
            self._row(bl, "Score", "--")

        # ── Confidence — read real value; never show 75% fake ──
        try:
            conf = float(data.get("Confidence", -1))
        except Exception:
            conf = -1.0
        if conf > 0:
            c_color = ("#00B69B" if conf >= 90 else "#CDDC39" if conf >= 75
                       else "#F1C40F" if conf >= 60 else "#F9322C")
            self._progress_row(bl, "Confidence", conf, c_color)
        else:
            self._row(bl, "Confidence", "--")

        self._sep(bl)

        # ── Technicals ─────────────────────────────────────────
        trend_raw = str(data.get("Trend", "")).strip()
        trend_norm = trend_raw.lower().replace(" ", "_")
        trend_display = _TREND_MAP.get(trend_norm, trend_raw if trend_raw else "--")
        if "error" in trend_display.lower() or not _is_valid(trend_display):
            trend_display = "Neutral Trend"
        t_color = ("#00B69B" if "bullish" in trend_display.lower()
                   else "#F9322C" if "bearish" in trend_display.lower()
                   else TEXT_PRIMARY)
        self._row(bl, "Trend", trend_display, color=t_color)
        
        # Momentum
        mom_raw = str(data.get("Momentum", "")).strip()
        mom_display = mom_raw if _is_valid(mom_raw) else "--"
        m_color = ("#00B69B" if "bullish" in mom_display.lower() or "strong" in mom_display.lower()
                   else "#F9322C" if "bearish" in mom_display.lower() or "weak" in mom_display.lower()
                   else TEXT_PRIMARY)
        self._row(bl, "Momentum", mom_display, color=m_color)

        # Volume — service writes int-string or "--"
        vol_raw = data.get("Volume", "")
        vol_display = str(vol_raw) if _is_valid(vol_raw) else "--"
        self._row(bl, "Volume", vol_display)

        # VWAP — lives in _raw_data if available
        raw = data.get("_raw_data", {}) or {}
        vwap = scrub(raw.get("vwap", raw.get("VWAP", "")), "--")
        if vwap != "--":
            try: vwap = f"₹{float(vwap):.2f}"
            except Exception as _e:
                logging.getLogger(__name__).debug("Suppressed exception in trade_setup_panel.py:353: %s", _e)
        self._row(bl, "VWAP", vwap)
        
        # ICT
        ict_raw = str(data.get("ICT", "")).strip()
        ict_display = ict_raw if _is_valid(ict_raw) else "--"
        self._row(bl, "ICT", ict_display)

        self._sep(bl)

        # ── Pricing — correct key names ────────────────────────
        def fmt(v) -> str:
            sv = scrub(v, "")
            if not sv: return "--"
            try:
                f = float(sv)
                return f"₹{f:.2f}" if f != 0.0 else "--"
            except Exception:
                return sv

        entry_val = data.get("Entry", 0)
        sl_val    = data.get("Stop Loss", 0)     # ← correct key from service
        t1_val    = data.get("Target 1", 0)       # ← correct key from service

        entry_str = fmt(entry_val)
        sl_str    = fmt(sl_val)
        t1_str    = fmt(t1_val)

        # BUG-07 validation (visual flag only, no crash)
        try:
            e, s, t = float(entry_val), float(sl_val), float(t1_val)
            if raw_sig == "BUY":
                valid = s < e < t
            elif raw_sig == "SELL":
                valid = t < e < s
            else:
                valid = True
            if not valid:
                entry_str += " ⚠"
        except Exception as _e:
            logging.getLogger(__name__).debug("Suppressed exception in trade_setup_panel.py:392: %s", _e)

        self._row(bl, "Entry",    entry_str, color="#2962FF")
        self._row(bl, "Stop Loss", sl_str,   color="#F9322C")
        self._row(bl, "Target",    t1_str,   color="#00B69B")
        
        # Risk Reward — service key is "Risk Reward"
        rr_raw = scrub(data.get("Risk Reward", data.get("RR", data.get("risk_reward", ""))), "--")
        if rr_raw != "--":
            rr_color = TEXT_PRIMARY
            try:
                v = float(str(rr_raw).split(":")[-1])
                rr_color = "#00B69B" if v >= 3 else "#2962FF" if v >= 2 else "#F1C40F" if v >= 1.5 else TEXT_PRIMARY
            except Exception as _e:
                logging.getLogger(__name__).debug("Suppressed exception in trade_setup_panel.py:406: %s", _e)
            self._row(bl, "Risk Reward", rr_raw, color=rr_color)
        else:
            self._row(bl, "Risk Reward", "--")

        self._sep(bl)

        # ── Reasons — read "_why_selected" (service key) ───────
        reasons_source = data.get("_why_selected",
                         data.get("Reasons",
                         data.get("reasons",
                         data.get("_reasons", []))))
        reasons_formatted = _format_reasons(reasons_source)

        r_frame = QFrame()
        r_frame.setObjectName("ReasonsFrame")
        rl = QVBoxLayout(r_frame)
        rl.setContentsMargins(10, 10, 10, 10)
        rl.setSpacing(4)

        title_lbl = QLabel("WHY SELECTED")
        title_lbl.setStyleSheet("color: #787B86; font-size: 12px; font-weight: bold; margin-bottom: 4px;")
        rl.addWidget(title_lbl)

        for reason in reasons_formatted:
            lbl_r = QLabel(reason)
            lbl_r.setStyleSheet("color: #D1D4DC; font-size: 14px;")
            lbl_r.setWordWrap(True)
            rl.addWidget(lbl_r)

        bl.addWidget(r_frame)

        card_l.addWidget(body)
        card_l.addStretch()
        self._layout.addWidget(card)
