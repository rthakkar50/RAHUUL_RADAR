import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt
from ui.styles import CARD_BG, COLOR_BUY, COLOR_SELL, COLOR_WATCH, TEXT_PRIMARY, TEXT_SECONDARY

logger = logging.getLogger(__name__)

class BestTradeCard(QFrame):
    """
    A modern card widget to display one of the 'Today's Best Trades' from the scanner.
    """
    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.data = data
        self._init_ui()
        
    def _init_ui(self):
        self.setStyleSheet(f"""
            BestTradeCard {{
                background-color: {CARD_BG};
                border: 1px solid #3D4047;
                border-radius: 8px;
            }}
            QLabel {{ color: {TEXT_PRIMARY}; }}
        """)
        self.setMinimumWidth(280)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # --- Header (Symbol & Signal) ---
        header_layout = QHBoxLayout()
        
        symbol = str(self.data.get("Symbol", "--"))
        lbl_symbol = QLabel(symbol)
        lbl_symbol.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_layout.addWidget(lbl_symbol)
        
        header_layout.addStretch()
        
        signal = str(self.data.get("Signal", "--"))
        lbl_signal = QLabel(signal)
        lbl_signal.setFont(QFont("Segoe UI", 12, QFont.Bold))
        sig_color = COLOR_BUY if 'BUY' in signal else COLOR_SELL if 'SELL' in signal else COLOR_WATCH
        lbl_signal.setStyleSheet(f"background-color: {sig_color}; padding: 4px 8px; border-radius: 4px;")
        header_layout.addWidget(lbl_signal)
        
        layout.addLayout(header_layout)
        
        # --- Metrics Row 1 ---
        m1_layout = QHBoxLayout()
        m1_layout.addWidget(self._create_metric_widget("Entry", f"{self.data.get('Entry', 0):.2f}"))
        m1_layout.addWidget(self._create_metric_widget("Stop Loss", f"{self.data.get('Stop Loss', 0):.2f}"))
        layout.addLayout(m1_layout)
        
        # --- Metrics Row 2 ---
        m2_layout = QHBoxLayout()
        m2_layout.addWidget(self._create_metric_widget("Target 1", f"{self.data.get('Target 1', 0):.2f}"))
        m2_layout.addWidget(self._create_metric_widget("Risk/Reward", str(self.data.get("Risk Reward", "--"))))
        layout.addLayout(m2_layout)
        
        # --- Metrics Row 3 ---
        m3_layout = QHBoxLayout()
        m3_layout.addWidget(self._create_metric_widget("Score", f"{self.data.get('Score', 0)}"))
        m3_layout.addWidget(self._create_metric_widget("Confidence", f"{self.data.get('Confidence', 0):.1f}%"))
        layout.addLayout(m3_layout)
        
        # --- Why Selected ---
        layout.addWidget(self._create_separator())
        lbl_why = QLabel("Why Selected:")
        lbl_why.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_why.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(lbl_why)
        
        reasons = self.data.get("_why_selected", [])
        if not reasons:
            reasons = ["No specific insights available."]
            
        for reason in reasons[:5]:
            lbl_r = QLabel(f"• {reason}")
            lbl_r.setFont(QFont("Segoe UI", 9))
            lbl_r.setWordWrap(True)
            layout.addWidget(lbl_r)

    def _create_metric_widget(self, title: str, value: str) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(2)
        
        lbl_t = QLabel(title)
        lbl_t.setFont(QFont("Segoe UI", 9))
        lbl_t.setStyleSheet("color: #888888;")
        l.addWidget(lbl_t)
        
        lbl_v = QLabel(value)
        lbl_v.setFont(QFont("Segoe UI", 11, QFont.Bold))
        l.addWidget(lbl_v)
        return w
        
    def _create_separator(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        f.setFrameShadow(QFrame.Sunken)
        f.setStyleSheet("background-color: #3D4047;")
        return f
