import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from ui.styles import BG_COLOR, CARD_BG
from ui.widgets.ai_decision_panel import AIDecisionPanel
from ui.widgets.trade_setup_panel import SmartTradeSetupPanel
from application.decision_explanation_service import DecisionExplanationService

logger = logging.getLogger(__name__)

class StockAnalysisPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.decision_service = DecisionExplanationService()
        self.setWindowTitle("Stock Analysis")
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_COLOR};
            }}
            QScrollArea {{ border: none; background: transparent; }}
        """)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Header for Symbol and Company Name
        from PySide6.QtWidgets import QLabel
        from PySide6.QtGui import QFont
        self.lbl_header = QLabel("Symbol - Company Name")
        self.lbl_header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.lbl_header.setStyleSheet("color: white; margin-bottom: 10px;")
        self.lbl_header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        
        # Horizontal layout for side-by-side panels
        scroll_layout = QHBoxLayout(content_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)

        self.smart_trade_setup_panel = SmartTradeSetupPanel()
        self.ai_decision_panel = AIDecisionPanel()

        scroll_layout.addWidget(self.smart_trade_setup_panel)
        scroll_layout.addWidget(self.ai_decision_panel)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def update_data(self, scan_result: dict):
        try:
            symbol = scan_result.get("Symbol", "Unknown")
            company = scan_result.get("Company", "")
            if company and company != symbol:
                title = f"{symbol} - {company}"
            else:
                title = symbol
            self.lbl_header.setText(title)

            # We skip the company name, tabs and empty widgets (Bug-4)
            # Just update the two core AI engines.
            
            # SPRINT-73 & FINAL V1.0: Map immutable generic dict to AI Decision Panel
            parsed_data = DecisionExplanationService().extract_decision_data(scan_result)
            self.ai_decision_panel.update_panel(parsed_data)
            self.smart_trade_setup_panel.update_panel(parsed_data)
            
        except Exception as e:
            import traceback
            logger.error(f"Error updating analysis dialog: {e}\n{traceback.format_exc()}")

    def show_panel(self):
        self.exec()

    def hide_panel(self):
        self.accept()
