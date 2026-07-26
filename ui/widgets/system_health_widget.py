from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class SystemHealthWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.lbl = QLabel("System Health: No Data")
        self.lbl.setStyleSheet("color: #A0AAB5; font-size: 14px; font-weight: bold;")
        self.layout.addWidget(self.lbl)
        self.refresh_health()

    def refresh_health(self, data: dict = None):
        try:
            if data is None:
                from application.diagnostics_service import DiagnosticsService
                service = DiagnosticsService()
                data = service.get_system_health()
            
            if data and "cpu_percent" in data and "memory_usage_mb" in data:
                cpu = data["cpu_percent"]
                mem = data["memory_usage_mb"]
                status = data.get("status", "ONLINE")
                self.lbl.setText(f"System Health: {status} | CPU: {cpu}% | RAM: {mem} MB")
                self.lbl.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: bold;")
            else:
                self.lbl.setText("System Health: No Data")
                self.lbl.setStyleSheet("color: #A0AAB5; font-size: 14px; font-weight: bold;")
        except Exception:
            self.lbl.setText("System Health: No Data")
            self.lbl.setStyleSheet("color: #A0AAB5; font-size: 14px; font-weight: bold;")
