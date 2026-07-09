from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from strategy.ptve_engine import PaperTradingValidationEngine

class PTVEPage(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = PaperTradingValidationEngine()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Paper Trading Validation Engine (PTVE)")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(header)
        
        desc = QLabel("Certification gate for Active Trading AI. Validates historical paper trades against strict performance metrics.")
        desc.setStyleSheet("color: #AAA;")
        layout.addWidget(desc)
        
        # Certification Banner
        self.banner = QLabel("CERTIFICATION STATUS: UNKNOWN")
        self.banner.setAlignment(Qt.AlignCenter)
        self.banner.setStyleSheet("background-color: #3D4047; color: white; padding: 20px; font-size: 20px; font-weight: bold; border-radius: 8px;")
        layout.addWidget(self.banner)
        
        # Refresh Button
        self.btn_refresh = QPushButton("Run Validation")
        self.btn_refresh.setFixedWidth(200)
        self.btn_refresh.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        self.btn_refresh.clicked.connect(self.run_validation)
        layout.addWidget(self.btn_refresh, alignment=Qt.AlignCenter)
        
        # Metrics Grid
        grid_frame = QFrame()
        grid = QGridLayout(grid_frame)
        grid.setSpacing(15)
        
        self.metrics_labels = {}
        
        def add_metric(row, col, title):
            box = QFrame()
            box.setStyleSheet("background-color: #1E2028; border: 1px solid #3D4047; border-radius: 8px;")
            box_layout = QVBoxLayout(box)
            
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet("color: #888; font-size: 12px; border: none;")
            lbl_title.setAlignment(Qt.AlignCenter)
            
            lbl_val = QLabel("--")
            lbl_val.setStyleSheet("color: white; font-size: 24px; font-weight: bold; border: none;")
            lbl_val.setAlignment(Qt.AlignCenter)
            
            box_layout.addWidget(lbl_title)
            box_layout.addWidget(lbl_val)
            
            grid.addWidget(box, row, col)
            self.metrics_labels[title] = lbl_val
            
        # Row 0
        add_metric(0, 0, "Total Trades")
        add_metric(0, 1, "Win Rate")
        add_metric(0, 2, "Profit Factor")
        add_metric(0, 3, "Expectancy")
        
        # Row 1
        add_metric(1, 0, "Wins / Losses")
        add_metric(1, 1, "Max Drawdown")
        add_metric(1, 2, "Avg Win")
        add_metric(1, 3, "Avg Loss")
        
        layout.addWidget(grid_frame)
        layout.addStretch()
        
        self.run_validation()
        
    def run_validation(self):
        report = self.engine.generate_certification_report()
        
        status = report.get("status", "UNKNOWN")
        if "READY" in status and "NOT" not in status:
            self.banner.setText(f"✅ {status} ✅")
            self.banner.setStyleSheet("background-color: rgba(76, 175, 80, 0.2); color: #4CAF50; border: 2px solid #4CAF50; padding: 20px; font-size: 20px; font-weight: bold; border-radius: 8px;")
        else:
            self.banner.setText(f"❌ {status} ❌")
            self.banner.setStyleSheet("background-color: rgba(244, 67, 54, 0.2); color: #F44336; border: 2px solid #F44336; padding: 20px; font-size: 20px; font-weight: bold; border-radius: 8px;")
            
        self.metrics_labels["Total Trades"].setText(str(report.get("total_trades", 0)))
        self.metrics_labels["Win Rate"].setText(f"{report.get('win_rate', 0)}%")
        self.metrics_labels["Profit Factor"].setText(str(report.get("profit_factor", 0)))
        self.metrics_labels["Expectancy"].setText(str(report.get("expectancy", 0)))
        
        self.metrics_labels["Wins / Losses"].setText(f"{report.get('wins', 0)} / {report.get('losses', 0)}")
        self.metrics_labels["Max Drawdown"].setText(f"₹{report.get('max_drawdown', 0)}")
        self.metrics_labels["Avg Win"].setText(f"₹{report.get('avg_win', 0)}")
        self.metrics_labels["Avg Loss"].setText(f"₹{report.get('avg_loss', 0)}")
