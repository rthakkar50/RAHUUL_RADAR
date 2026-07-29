from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from ui.intraday_scanner import IntradayScannerPage
import logging

logger = logging.getLogger(__name__)

class ActiveTradingScannerPage(QWidget):
    """
    Active Trading Scanner: Unified high-performance scanner for both
    ⚡ Scalping (1m/3m momentum) and 📈 Intraday (5m/15m trend breakouts).
    """
    navigate_to_chart = Signal(str)
    
    def __init__(self, mode_name="ActiveTrading", engine=None):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Unified Intraday & Scalping Scanner Page
        self.scanner_page = IntradayScannerPage()
        if hasattr(self.scanner_page, 'navigate_to_chart'):
            self.scanner_page.navigate_to_chart.connect(self.navigate_to_chart.emit)
            
        self.main_layout.addWidget(self.scanner_page)
