from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class WatchlistPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.lbl = QLabel("Watchlist Panel - Auto Sync Enabled")
        self.layout.addWidget(self.lbl)
        
    def refresh_data(self):
        pass
