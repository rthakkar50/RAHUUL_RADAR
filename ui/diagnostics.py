from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea
from PySide6.QtCore import Qt, QThread, Signal
from ui.styles import CARD_BG, TEXT_PRIMARY, BTN_BLUE, BG_COLOR
import sys
import os
import time
import psutil
from datetime import datetime

from utils.platform_actions import open_path
from config.settings import BASE_DIR
from core.pce_auditor import ProductionCertificationEngine

class DiagnosticsWorker(QThread):
    progress = Signal(str, str, str) # name, status, message
    finished = Signal(bool)
    
    def run(self):
        all_passed = True
        
        # 1. Config Check
        try:
            from core.config_manager import ConfigManager
            cm = ConfigManager()
            self.progress.emit("Config", "PASS", "config.json loaded successfully.")
        except Exception as e:
            self.progress.emit("Config", "FAIL", str(e))
            all_passed = False
            
        # 2. Database Check
        try:
            from application.database import DatabaseManager
            db = DatabaseManager()
            self.progress.emit("Journal Database", "PASS", "radar.db accessible and ready.")
        except Exception as e:
            self.progress.emit("Journal Database", "FAIL", str(e))
            all_passed = False
            
        # 3. Export Folder
        try:
            exports = os.path.join(str(BASE_DIR), "exports")
            os.makedirs(exports, exist_ok=True)
            test_file = os.path.join(exports, ".test")
            with open(test_file, 'w') as f:
                f.write("ok")
            os.remove(test_file)
            self.progress.emit("Export Folder", "PASS", f"Path: {exports} | Write permissions verified.")
        except Exception as e:
            self.progress.emit("Export Folder", "FAIL", str(e))
            all_passed = False
            
        # 3b. Log Folder
        try:
            logs = os.path.join(str(BASE_DIR), "logs")
            os.makedirs(logs, exist_ok=True)
            self.progress.emit("Log Folder", "PASS", "logs/ folder accessible.")
        except Exception as e:
            self.progress.emit("Log Folder", "FAIL", str(e))
            all_passed = False
            
        # 4. Scanner Engine
        try:
            from scanner.scanner_engine import ScannerEngine
            self.progress.emit("Scanner Engine", "PASS", "Modules loaded.")
        except Exception as e:
            self.progress.emit("Scanner Engine", "FAIL", str(e))
            all_passed = False
            
        # 5. Backtest Engine
        try:
            from backtest.backtest_orchestrator import BacktestOrchestrator
            self.progress.emit("Backtest Engine", "PASS", "Modules loaded.")
        except Exception as e:
            self.progress.emit("Backtest Engine", "FAIL", str(e))
            all_passed = False
            
        # 6. Yahoo Connection
        try:
            import yfinance as yf
            start_t = time.time()
            df = yf.download("RELIANCE.NS", period="1d", progress=False)
            end_t = time.time()
            if not df.empty:
                lat = round(end_t - start_t, 2)
                self.progress.emit("Yahoo Finance", "PASS", f"Connected | Latency : {lat} sec")
            else:
                self.progress.emit("Yahoo Finance", "WARN", "Connected, but no data returned.")
        except Exception as e:
            self.progress.emit("Yahoo Connection", "FAIL", str(e))
            all_passed = False
            
        self.finished.emit(all_passed)

class DiagnosticsScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title = QLabel("System Diagnostics")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {TEXT_PRIMARY};")
        layout.addWidget(title)
        
        self.overall_status = QLabel("Overall Health: Awaiting Scan...")
        self.overall_status.setStyleSheet("font-size: 16px; color: #A0AAB5;")
        layout.addWidget(self.overall_status)
        
        # Container
        self.container = QFrame()
        self.container.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 8px;")
        container_layout = QVBoxLayout(self.container)
        
        self.results_layout = QVBoxLayout()
        container_layout.addLayout(self.results_layout)
        container_layout.addStretch()
        
        layout.addWidget(self.container)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_log = QPushButton("Open Log")
        self.btn_log.setStyleSheet(f"background-color: #3D4047; color: white; font-weight: bold; padding: 12px; border-radius: 4px; border: none;")
        log_path = os.path.join(str(BASE_DIR), "logs", "app.log")
        self.btn_log.clicked.connect(lambda: open_path(log_path))
        
        self.btn_run = QPushButton("Run Diagnostics")
        self.btn_run.setStyleSheet(f"background-color: {BTN_BLUE}; color: white; font-weight: bold; padding: 12px; border-radius: 4px; border: none;")
        self.btn_run.clicked.connect(self.run_diagnostics)
        
        self.btn_pce = QPushButton("Run Production Certification (PCE)")
        self.btn_pce.setStyleSheet(f"background-color: #9C27B0; color: white; font-weight: bold; padding: 12px; border-radius: 4px; border: none;")
        self.btn_pce.clicked.connect(self.run_pce_audit)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_log)
        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.btn_pce)
        
        layout.addLayout(btn_layout)
        
    def add_result(self, name, status, message):
        row = QFrame()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(10, 5, 10, 5)
        
        name_lbl = QLabel(name)
        name_lbl.setFixedWidth(150)
        name_lbl.setStyleSheet(f"font-weight: bold; color: {TEXT_PRIMARY};")
        
        status_lbl = QLabel(f"[{status}]")
        status_lbl.setFixedWidth(60)
        if status == "PASS":
            status_lbl.setStyleSheet("color: #4CAF50; font-weight: bold;")
        elif status == "FAIL":
            status_lbl.setStyleSheet("color: #F44336; font-weight: bold;")
        else:
            status_lbl.setStyleSheet("color: #FFC107; font-weight: bold;")
            
        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet("color: #A0AAB5;")
        
        row_layout.addWidget(name_lbl)
        row_layout.addWidget(status_lbl)
        row_layout.addWidget(msg_lbl)
        row_layout.addStretch()
        
        self.results_layout.addWidget(row)
        
    def run_diagnostics(self):
        # Clear old results
        for i in reversed(range(self.results_layout.count())): 
            self.results_layout.itemAt(i).widget().setParent(None)
            
        self.btn_run.setEnabled(False)
        self.btn_run.setText("Running Checks...")
        self.overall_status.setText("Overall Health: SCANNING...")
        self.overall_status.setStyleSheet("font-size: 16px; color: #FFC107;")
        
        self.worker = DiagnosticsWorker()
        self.worker.progress.connect(self.add_result)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
        
    def on_finished(self, passed):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("Run Diagnostics")
        
        last_checked = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        
        if passed:
            self.overall_status.setText(f"Overall Health : 100% HEALTHY\n\nLast Checked :\n{last_checked}")
            self.overall_status.setStyleSheet("font-size: 16px; color: #4CAF50; font-weight: bold;")
        else:
            self.overall_status.setText(f"Overall Health : ISSUES DETECTED\n\nLast Checked :\n{last_checked}")
            self.overall_status.setStyleSheet("font-size: 16px; color: #F44336; font-weight: bold;")
            
    def run_pce_audit(self):
        from PySide6.QtWidgets import QMessageBox
        self.btn_pce.setEnabled(False)
        self.btn_pce.setText("Running PCE Audit...")
        
        try:
            pce = ProductionCertificationEngine()
            report_str = pce.run_full_audit()
            
            # Save report
            report_path = "pce_audit_report.md"
            with open(report_path, "w") as f:
                f.write(report_str)
                
            QMessageBox.information(self, "PCE Audit Complete", f"Audit generated and saved to {report_path}.")
            open_path(report_path)
        except Exception as e:
            QMessageBox.critical(self, "PCE Audit Failed", str(e))
            
        self.btn_pce.setEnabled(True)
        self.btn_pce.setText("Run Production Certification (PCE)")
