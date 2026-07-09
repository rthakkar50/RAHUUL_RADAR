from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class LogViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.lbl = QLabel("Live Log Viewer (Tailing radar.log)")
        self.layout.addWidget(self.lbl)
