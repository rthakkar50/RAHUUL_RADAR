from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class PerformanceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.lbl = QLabel("Performance Metrics: Load 45ms")
        self.layout.addWidget(self.lbl)
