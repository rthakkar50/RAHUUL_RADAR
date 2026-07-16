from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDateEdit, QCheckBox, QFrame, QGridLayout, QSpinBox, QMessageBox, QProgressBar
from PySide6.QtCore import Qt, QDate, QTimer, QThread, Signal
import csv
import sys
import subprocess
import os
from ui.styles import CARD_BG, TEXT_PRIMARY, BTN_BLUE, BG_COLOR
from utils.logger import get_logger
from data.stocks import TOP_50_STOCKS

logger = get_logger(__name__)

from backtest.engine_wrapper import BacktestWrapperThread

class BacktestWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backtest Engine")
        self.resize(450, 650)
        self.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_PRIMARY};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("BACKTEST")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Configuration Card
        config_card = QFrame()
        config_card.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 8px;")
        config_layout = QVBoxLayout(config_card)
        
        # Dates
        date_layout = QGridLayout()
        
        lbl_start = QLabel("Start Date :")
        self.dt_start = QDateEdit()
        self.dt_start.setDate(QDate(2025, 1, 1))
        self.dt_start.setDisplayFormat("dd-MM-yyyy")
        self.dt_start.setCalendarPopup(True)
        self.dt_start.setStyleSheet("background-color: #161B22; color: #E6EDF3; padding: 6px; border: 1px solid #30363D; border-radius: 4px;")
        
        lbl_end = QLabel("End Date :")
        lbl_end.setStyleSheet("font-weight: bold; color: #8B949E;")
        self.dt_end = QDateEdit()
        self.dt_end.setDate(QDate.currentDate())
        self.dt_end.setDisplayFormat("dd-MM-yyyy")
        self.dt_end.setCalendarPopup(True)
        self.dt_end.setStyleSheet("background-color: #161B22; color: #E6EDF3; padding: 6px; border: 1px solid #30363D; border-radius: 4px;")
        
        date_layout.addWidget(lbl_start, 0, 0)
        date_layout.addWidget(self.dt_start, 0, 1)
        date_layout.addWidget(lbl_end, 1, 0)
        date_layout.addWidget(self.dt_end, 1, 1)
        config_layout.addLayout(date_layout)
        
        # Symbols
        lbl_symbols = QLabel("Symbols")
        lbl_symbols.setStyleSheet("font-weight: bold; margin-top: 10px;")
        config_layout.addWidget(lbl_symbols)
        
        sym_layout = QHBoxLayout()
        self.chk_top50 = QCheckBox("Top 50 NSE")
        self.chk_top50.setChecked(True)
        self.chk_custom = QCheckBox("Custom Symbols")
        
        sym_layout.addWidget(self.chk_top50)
        sym_layout.addWidget(self.chk_custom)
        sym_layout.addStretch()
        config_layout.addLayout(sym_layout)
        
        # Holding Days
        holding_layout = QHBoxLayout()
        lbl_holding = QLabel("Holding Days :")
        lbl_holding.setStyleSheet("font-weight: bold; color: #8B949E;")
        self.spin_holding = QSpinBox()
        self.spin_holding.setValue(5)
        self.spin_holding.setRange(1, 365)
        self.spin_holding.setStyleSheet("background-color: #161B22; color: #E6EDF3; padding: 6px; border: 1px solid #30363D; border-radius: 4px;")
        holding_layout.addWidget(lbl_holding)
        holding_layout.addWidget(self.spin_holding)
        holding_layout.addStretch()
        config_layout.addLayout(holding_layout)
        
        # Run Button
        self.btn_run = QPushButton("⚡ Run Backtest")
        self.btn_run.setStyleSheet("background-color: #238636; color: white; font-weight: bold; padding: 10px 16px; border-radius: 4px; margin-top: 10px;")
        self.btn_run.clicked.connect(self.run_backtest)
        config_layout.addWidget(self.btn_run)
        
        # Status Label
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #888; font-size: 13px;")
        config_layout.addWidget(self.lbl_status)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3D4047; border-radius: 4px;
                background-color: #1A1C23; text-align: center; color: white;
            }
            QProgressBar::chunk { background-color: #2196F3; border-radius: 4px; }
        """)
        layout.addWidget(self.progress_bar)
        
        self.btn_run = QPushButton("Run Backtest")
        self.btn_run.setStyleSheet(f"background-color: {BTN_BLUE}; color: white; font-weight: bold; border: none; margin-top: 10px;")
        self.btn_run.clicked.connect(self.run_backtest)
        config_layout.addWidget(self.btn_run)
        
        layout.addWidget(config_card)
        
        # Results Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #3D4047;")
        layout.addWidget(line)
        
        # Results Area
        self.res_card = QFrame()
        self.res_card.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 8px;")
        res_layout = QGridLayout(self.res_card)
        
        res_layout.addWidget(QLabel("BUY Win Rate"), 0, 0)
        self.val_buy_win = QLabel("--")
        self.val_buy_win.setStyleSheet("font-weight: bold;")
        res_layout.addWidget(self.val_buy_win, 0, 1)
        
        res_layout.addWidget(QLabel("SELL Win Rate"), 1, 0)
        self.val_sell_win = QLabel("--")
        self.val_sell_win.setStyleSheet("font-weight: bold;")
        res_layout.addWidget(self.val_sell_win, 1, 1)
        
        res_layout.addWidget(QLabel("Overall Win Rate"), 2, 0)
        self.val_ovr_win = QLabel("--")
        self.val_ovr_win.setStyleSheet("font-weight: bold;")
        res_layout.addWidget(self.val_ovr_win, 2, 1)
        
        res_layout.addWidget(QLabel("Profit Factor"), 3, 0)
        self.val_pf = QLabel("--")
        self.val_pf.setStyleSheet("font-weight: bold;")
        res_layout.addWidget(self.val_pf, 3, 1)
        
        res_layout.addWidget(QLabel("Average Return"), 4, 0)
        self.val_ret = QLabel("--")
        self.val_ret.setStyleSheet("font-weight: bold;")
        res_layout.addWidget(self.val_ret, 4, 1)
        
        res_layout.addWidget(QLabel("Execution Time"), 5, 0)
        self.val_time = QLabel("--")
        self.val_time.setStyleSheet("font-weight: bold;")
        res_layout.addWidget(self.val_time, 5, 1)
        
        layout.addWidget(self.res_card)
        
        # Export Button
        self.btn_export = QPushButton("Export CSV")
        self.btn_export.setStyleSheet("background-color: transparent; border: 1px solid #4CAF50; color: #4CAF50; font-weight: bold;")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.export_csv)
        layout.addWidget(self.btn_export)
        
        self.last_trades = []
        
        layout.addStretch()

    def run_backtest(self):
        self.btn_run.setText("Running...")
        self.btn_run.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        symbols = [f"{s.symbol}.NS" for s in TOP_50_STOCKS] if self.chk_top50.isChecked() else ["RELIANCE.NS", "TCS.NS"]
        
        hold_days = self.spin_holding.value()
        start = self.dt_start.date().toString("yyyy-MM-dd")
        end = self.dt_end.date().toString("yyyy-MM-dd")
        
        self.engine = BacktestWrapperThread(symbols, start, end, hold_days)
        self.engine.progress.connect(self.update_progress)
        self.engine.error.connect(self.backtest_error)
        self.engine.finished.connect(self.backtest_finished)
        self.engine.start()

    def update_progress(self, text, val):
        self.lbl_status.setText(text)
        self.progress_bar.setValue(val)
        
    def backtest_error(self, err_msg):
        QMessageBox.warning(self, "Backtest Error", err_msg)
        self.btn_run.setText("Run Backtest")
        self.lbl_status.setText("")
        self.btn_run.setEnabled(True)
        self.progress_bar.setVisible(False)
        
    def backtest_finished(self, result):
        self.val_buy_win.setText(f"{result.get('buy_win', 0)}%")
        self.val_buy_win.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        self.val_sell_win.setText(f"{result.get('sell_win', 0)}%")
        self.val_sell_win.setStyleSheet("color: #F44336; font-weight: bold;")
        
        self.val_ovr_win.setText(f"{result.get('overall_win', 0)}%")
        self.val_ovr_win.setStyleSheet("color: #2196F3; font-weight: bold;")
        
        self.val_pf.setText(str(result.get('profit_factor', 0)))
        self.val_ret.setText(f"{result.get('avg_return', 0)}%")
        self.val_ret.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        self.val_time.setText(f"{result.get('exec_time', 0)}s")
        
        self.progress_bar.setVisible(False)
        self.lbl_status.setText("Backtest Complete.")
        self.btn_run.setText("Run Backtest")
        self.btn_run.setEnabled(True)
        self.btn_export.setEnabled(True)

    def export_csv(self):
        from config.settings import BASE_DIR
        exports_dir = os.path.join(str(BASE_DIR), "exports")
        if not os.path.exists(exports_dir):
            QMessageBox.information(self, "Export", "No exports directory found yet.")
            return
            
        try:
            if sys.platform == "darwin":
                subprocess.call(["open", exports_dir])
            elif sys.platform == "win32":
                os.startfile(exports_dir)
            else:
                subprocess.call(["xdg-open", exports_dir])
        except Exception as e:
            QMessageBox.warning(self, "Export Failed", f"Could not open directory:\n{e}")
