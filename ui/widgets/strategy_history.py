from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class StrategyHistory(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.lbl = QLabel("Strategy History - Saved Configurations")
        self.layout.addWidget(self.lbl)
