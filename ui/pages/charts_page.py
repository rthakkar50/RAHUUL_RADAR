from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.widgets.chart_toolbar import ChartToolbar
from ui.widgets.chart_panel import ChartPanel
from application.chart_service import ChartService

class ChartsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = ChartService()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.toolbar = ChartToolbar()
        self.layout.addWidget(self.toolbar)
        
        self.chart = ChartPanel()
        self.layout.addWidget(self.chart)
