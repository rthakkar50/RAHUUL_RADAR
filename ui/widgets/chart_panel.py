from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class ChartPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_empty = QLabel("No Chart Data Available")
        self.lbl_empty.setStyleSheet("font-size: 16px; color: #888; font-weight: bold; background-color: #1A1C20;")
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl_empty)
        
    def load_data(self, data: dict):
        if not data or not data.get("candles"):
            self.lbl_empty.show()
        else:
            self.lbl_empty.hide()
            # Render native drawing logic here
            pass
