from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class StrategyPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.lbl = QLabel("Strategy Preview - Flow Visualizer")
        self.layout.addWidget(self.lbl)
