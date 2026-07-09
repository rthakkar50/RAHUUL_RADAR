from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from ui.widgets.strategy_builder import StrategyBuilder
from ui.widgets.strategy_preview import StrategyPreview
from ui.widgets.strategy_results import StrategyResults
from ui.widgets.strategy_history import StrategyHistory
from application.strategy_lab_service import StrategyLabService

class StrategyLabPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = StrategyLabService()
        
        self.layout = QHBoxLayout(self)
        
        # Left: Builder
        self.builder = StrategyBuilder()
        self.layout.addWidget(self.builder, 1)
        
        # Center: Preview
        self.preview = StrategyPreview()
        self.layout.addWidget(self.preview, 2)
        
        # Right: Results & History
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.results = StrategyResults()
        self.history = StrategyHistory()
        right_layout.addWidget(self.results)
        right_layout.addWidget(self.history)
        self.layout.addWidget(right_panel, 1)
