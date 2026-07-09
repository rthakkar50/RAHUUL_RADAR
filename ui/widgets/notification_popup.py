from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer

class NotificationPopup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.lbl = QLabel("Alert")
        self.layout.addWidget(self.lbl)
        self.setStyleSheet("background-color: #2D2F34; border: 1px solid #555; border-radius: 8px;")
        
    def show_alert(self, title, message, duration_ms=3000):
        self.lbl.setText(f"<b>{title}</b><br>{message}")
        self.show()
        QTimer.singleShot(duration_ms, self.hide)
