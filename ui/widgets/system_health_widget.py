from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class SystemHealthWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.lbl = QLabel("System Health: CPU 12% | RAM 400MB")
        self.layout.addWidget(self.lbl)
