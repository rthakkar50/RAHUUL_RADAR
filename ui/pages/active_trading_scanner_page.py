from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from ui.intraday_scanner import IntradayScannerPage
from ui.pages.scalping_scanner_page import ScalpingScannerPage
import logging

logger = logging.getLogger(__name__)

class ActiveTradingScannerPage(QWidget):
    """
    Active Trading Scanner acts as a unified container for
    Intraday and Scalping modes.
    """
    navigate_to_chart = Signal(str)
    
    def __init__(self, mode_name="ActiveTrading", engine=None):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # 1. Header
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("Active Trading Scanner")
        self.lbl_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)
        
        # 2. Tabs for Intraday and Scalping
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #3D4047;
                border-radius: 8px;
                background-color: #121418;
            }
            QTabBar::tab {
                background: #1A1C20;
                color: #888888;
                padding: 10px 25px;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #3D4047;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #2196F3;
                color: white;
            }
        """)
        
        # Initialize sub-pages
        self.intraday_page = IntradayScannerPage()
        self.scalping_page = ScalpingScannerPage()
        
        # We need to hide the title headers in the sub-pages to prevent duplicate titles
        if hasattr(self.intraday_page, 'lbl_title'):
            self.intraday_page.lbl_title.hide()
        if hasattr(self.scalping_page, 'lbl_title'):
            self.scalping_page.lbl_title.hide()
            
        # Hook up navigation signals if any are still needed
        self.intraday_page.navigate_to_chart.connect(self.navigate_to_chart.emit)
        self.scalping_page.navigate_to_chart.connect(self.navigate_to_chart.emit)
        
        self.tabs.addTab(self.intraday_page, "Intraday Mode")
        self.tabs.addTab(self.scalping_page, "Scalping Mode")
        
        self.main_layout.addWidget(self.tabs)
