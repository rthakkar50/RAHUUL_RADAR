from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.widgets.system_health_widget import SystemHealthWidget
from ui.widgets.module_status_widget import ModuleStatusWidget
from ui.widgets.log_viewer import LogViewer
from ui.widgets.performance_widget import PerformanceWidget
from application.diagnostics_service import DiagnosticsService

class DiagnosticsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = DiagnosticsService()
        self.layout = QVBoxLayout(self)
        
        self.lbl = QLabel("Enterprise Diagnostics Center")
        self.layout.addWidget(self.lbl)
        
        self.sys_health = SystemHealthWidget()
        self.mod_health = ModuleStatusWidget()
        self.perf = PerformanceWidget()
        self.logs = LogViewer()
        
        self.layout.addWidget(self.sys_health)
        self.layout.addWidget(self.mod_health)
        self.layout.addWidget(self.perf)
        self.layout.addWidget(self.logs)
