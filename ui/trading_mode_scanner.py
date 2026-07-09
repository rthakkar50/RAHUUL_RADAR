from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class TradingModeScanner(QWidget):
    """
    Empty placeholder page for Trading Modes (Phase 1).
    """
    def __init__(self, mode_name: str, engine=None):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl = QLabel(f"🚧 {mode_name} Scanner Page (Under Construction) 🚧")
        lbl.setStyleSheet("font-size: 24px; color: #888; font-weight: bold;")
        lbl.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(lbl)
