from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.styles import COLOR_BUY, COLOR_SELL, COLOR_WATCH

class TradeLevelsOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(32, 33, 36, 0.7);
                border-radius: 6px;
            }
            QLabel { color: #ccc; font-size: 11px; }
        """)
        self._init_ui()

    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(4)
        
        self.lbl_title = QLabel("OVERLAYS & INDICATORS")
        self.lbl_title.setStyleSheet("color: white; font-weight: bold;")
        self.layout.addWidget(self.lbl_title)
        
        self.labels = {}
        for key in ["EMA", "VWAP", "Volume", "ATR", "Support", "Resistance", 
                    "Swing High", "Swing Low", "AI Entry", "AI Stop Loss", 
                    "AI Target-1", "AI Target-2", "AI Target-3", "Trailing Stop"]:
            lbl = QLabel(f"{key}: N/A")
            self.labels[key] = lbl
            self.layout.addWidget(lbl)

    def update_overlays(self, data: dict):
        # Update the display values from the service data
        o = data.get("overlays", {})
        
        self._set_label("EMA", "Active", COLOR_WATCH if o.get("ema") else "#555")
        self._set_label("VWAP", "Active", COLOR_WATCH if o.get("vwap") else "#555")
        self._set_label("Volume", "Active", "#888" if o.get("volume") else "#555")
        self._set_label("ATR", "Active", "#888" if o.get("atr") else "#555")
        
        self._set_label("Support", o.get("support", "N/A"), "#4A90E2")
        self._set_label("Resistance", o.get("resistance", "N/A"), "#E24A4A")
        self._set_label("Swing High", o.get("swing_high", "N/A"), "#ccc")
        self._set_label("Swing Low", o.get("swing_low", "N/A"), "#ccc")
        
        self._set_label("AI Entry", o.get("ai_entry", "N/A"), COLOR_WATCH)
        self._set_label("AI Stop Loss", o.get("ai_sl", "N/A"), COLOR_SELL)
        self._set_label("AI Target-1", o.get("ai_t1", "N/A"), COLOR_BUY)
        self._set_label("AI Target-2", o.get("ai_t2", "N/A"), COLOR_BUY)
        self._set_label("AI Target-3", o.get("ai_t3", "N/A"), COLOR_BUY)
        self._set_label("Trailing Stop", o.get("trailing_stop", "N/A"), COLOR_SELL)

    def _set_label(self, key: str, val: str, color: str):
        if key in self.labels:
            if isinstance(val, (int, float)):
                val = f"{val:.2f}"
            self.labels[key].setText(f"{key}: {val}")
            self.labels[key].setStyleSheet(f"color: {color}; font-weight: bold;")
