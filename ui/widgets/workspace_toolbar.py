from PySide6.QtWidgets import QFrame, QHBoxLayout, QComboBox, QLabel

class WorkspaceToolbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.lbl = QLabel("Active Workspace:")
        self.combo = QComboBox()
        self.combo.addItems(["Swing Trading", "Intraday Trading", "Scalping", "Options"])
        self.layout.addWidget(self.lbl)
        self.layout.addWidget(self.combo)
