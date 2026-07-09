from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class PriorityQueuePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.lbl = QLabel("Priority Queue Panel - Auto Sync Enabled")
        self.layout.addWidget(self.lbl)
        
    def update_queue(self, scan_results):
        # Implementation is hooked into PriorityQueueService
        pass
