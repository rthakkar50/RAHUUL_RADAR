from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame, QButtonGroup
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.styles import CARD_BG, BTN_BLUE

class ChartToolbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #202124;
                border-bottom: 1px solid #3D4047;
            }}
            QPushButton {{
                background-color: transparent;
                color: #A0AAB5;
                border: 1px solid transparent;
                padding: 4px 10px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2D2F34;
                color: white;
            }}
            QPushButton:checked {{
                background-color: {CARD_BG};
                color: {BTN_BLUE};
                border: 1px solid {BTN_BLUE};
            }}
            QLabel {{ color: white; font-weight: bold; padding: 0 10px; }}
        """)
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)

        # Tools
        layout.addWidget(QLabel("Tools:"))
        for text in ["Zoom", "Reset", "Crosshair", "Draw", "Screenshot", "Export"]:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)

        layout.addSpacing(20)

        # Timeframes
        layout.addWidget(QLabel("Timeframe:"))
        self.tf_group = QButtonGroup(self)
        self.tf_group.setExclusive(True)
        
        tfs = ["1m", "3m", "5m", "15m", "1H", "4H", "Daily", "Weekly", "Monthly"]
        for tf in tfs:
            btn = QPushButton(tf)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            if tf == "Daily":
                btn.setChecked(True)
            self.tf_group.addButton(btn)
            layout.addWidget(btn)

        layout.addStretch()
