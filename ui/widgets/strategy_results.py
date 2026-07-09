from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class StrategyResults(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.lbl = QLabel("Strategy Results - Performance Metrics")
        self.layout.addWidget(self.lbl)
