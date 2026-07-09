from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class WorkspaceManagerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.lbl = QLabel("Workspace Manager")
        self.layout.addWidget(self.lbl)
