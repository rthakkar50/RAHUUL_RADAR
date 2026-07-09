from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ModuleStatusWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.lbl = QLabel("Module Status: All Engines ONLINE")
        self.layout.addWidget(self.lbl)
