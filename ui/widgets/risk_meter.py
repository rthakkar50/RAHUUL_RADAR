from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.styles import COLOR_BUY, COLOR_SELL, COLOR_WATCH

class RiskMeter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_level = QLabel("Risk Level: Medium")
        self.lbl_level.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.layout.addWidget(self.lbl_level)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(10)
        self.progress.setStyleSheet("QProgressBar { border-radius: 5px; background-color: #333; }")
        self.layout.addWidget(self.progress)
        
        metrics_layout = QHBoxLayout()
        self.lbl_capital = QLabel("Capital Risk: N/A")
        self.lbl_volatility = QLabel("Volatility: N/A")
        self.lbl_atr = QLabel("ATR Risk: N/A")
        
        for lbl in [self.lbl_capital, self.lbl_volatility, self.lbl_atr]:
            lbl.setStyleSheet("color: #aaa; font-size: 10px;")
            metrics_layout.addWidget(lbl)
            
        self.layout.addLayout(metrics_layout)
        
    def update_data(self, data: dict):
        level = data.get("level", "Medium").title()
        self.lbl_level.setText(f"Risk Level: {level}")
        
        val = 50
        color = COLOR_WATCH
        if "LOW" in level.upper(): val, color = 20, COLOR_BUY
        elif "HIGH" in level.upper(): val, color = 80, COLOR_SELL
        elif "EXTREME" in level.upper(): val, color = 95, "#FF0000"
            
        self.progress.setValue(val)
        self.progress.setStyleSheet(f"QProgressBar {{ border-radius: 5px; background-color: #333; }} QProgressBar::chunk {{ background-color: {color}; border-radius: 5px; }}")
        
        self.lbl_capital.setText(f"Capital Risk: {data.get('capital_risk')}")
        self.lbl_volatility.setText(f"Volatility: {data.get('volatility')}")
        self.lbl_atr.setText(f"ATR Risk: {data.get('atr_risk')}")
