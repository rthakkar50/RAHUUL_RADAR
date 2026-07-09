from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QComboBox, QLineEdit, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QFrame, QProgressBar)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QBrush, QColor
from ui.styles import BG_COLOR, CARD_BG, BTN_BLUE, COLOR_BUY, COLOR_WATCH, COLOR_SELL
from ui.widgets.scalping_results_table import ScalpingResultsTable
from application.scalping_scanner_service import ScalpingScannerService
import os
import logging
import time

logger = logging.getLogger(__name__)

class ScalpingScanWorker(QThread):
    progress = Signal(int)
    results_ready = Signal(list)
    
    def __init__(self, service, timeframe):
        super().__init__()
        self.service = service
        self.timeframe = timeframe
        
    def run(self):
        try:
            results = self.service.execute_scalping_scan(self.timeframe, self.progress.emit)
            self.results_ready.emit(results)
        except Exception as e:
            logger.error(f"Worker failed: {e}")
            self.results_ready.emit([])

class ScalpingScannerPage(QWidget):
    navigate_to_chart = Signal(str)
    
    def __init__(self, mode_name="Scalping", engine=None):
        super().__init__()
        self.service = ScalpingScannerService()
        self.scan_results = []
        self.worker = None
        self._init_ui()
        
        # Setup auto refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.run_scan)
        
    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # 1. Header
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("Scalping Scanner")
        self.lbl_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)
        
        # 2. Top Filter Bar
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 8px; border: 1px solid #3D4047;")
        filter_layout_main = QVBoxLayout(filter_frame)
        filter_layout_main.setContentsMargins(10, 10, 10, 10)
        filter_layout_main.setSpacing(10)
        
        top_row = QHBoxLayout()
        bottom_row = QHBoxLayout()
        
        # Index & Exchange
        top_row.addWidget(QLabel("Index:"))
        self.combo_index = QComboBox()
        self.combo_index.addItems(["All", "Nifty 50", "Nifty Bank"])
        self.combo_index.setStyleSheet("background-color: #202124; border: 1px solid #3D4047; padding: 4px; color: white;")
        top_row.addWidget(self.combo_index)
        
        top_row.addWidget(QLabel("Exchange:"))
        self.combo_exchange = QComboBox()
        self.combo_exchange.addItems(["NSE", "BSE"])
        self.combo_exchange.setStyleSheet("background-color: #202124; border: 1px solid #3D4047; padding: 4px; color: white;")
        top_row.addWidget(self.combo_exchange)
        
        # Sector
        top_row.addWidget(QLabel("Sector:"))
        self.combo_sector = QComboBox()
        self.combo_sector.addItems(["All", "BANKING", "IT", "AUTO", "PHARMA", "METAL", "FMCG", "ENERGY", "REALTY", "INFRASTRUCTURE"])
        self.combo_sector.setStyleSheet("background-color: #202124; border: 1px solid #3D4047; padding: 4px; color: white;")
        self.combo_sector.currentTextChanged.connect(self.apply_filters)
        top_row.addWidget(self.combo_sector)
        
        # Min Volume
        top_row.addWidget(QLabel("Min Vol:"))
        self.txt_min_vol = QLineEdit()
        self.txt_min_vol.setPlaceholderText("0")
        self.txt_min_vol.setStyleSheet("background-color: #202124; border: 1px solid #3D4047; padding: 4px; color: white;")
        self.txt_min_vol.textChanged.connect(self.apply_filters)
        top_row.addWidget(self.txt_min_vol)
        
        # Price Range
        top_row.addWidget(QLabel("Min Price:"))
        self.txt_min_price = QLineEdit()
        self.txt_min_price.setPlaceholderText("0")
        self.txt_min_price.setStyleSheet("background-color: #202124; border: 1px solid #3D4047; padding: 4px; color: white;")
        self.txt_min_price.textChanged.connect(self.apply_filters)
        top_row.addWidget(self.txt_min_price)
        
        top_row.addWidget(QLabel("Max Price:"))
        self.txt_max_price = QLineEdit()
        self.txt_max_price.setPlaceholderText("Inf")
        self.txt_max_price.setStyleSheet("background-color: #202124; border: 1px solid #3D4047; padding: 4px; color: white;")
        self.txt_max_price.textChanged.connect(self.apply_filters)
        top_row.addWidget(self.txt_max_price)
        top_row.addStretch()
        
        # Signal Type
        bottom_row.addWidget(QLabel("Signal:"))
        self.combo_signal = QComboBox()
        self.combo_signal.addItems(["All", "BUY", "SELL", "WATCH"])
        self.combo_signal.setStyleSheet("background-color: #202124; border: 1px solid #3D4047; padding: 4px; color: white;")
        self.combo_signal.currentTextChanged.connect(self.apply_filters)
        bottom_row.addWidget(self.combo_signal)
        
        # Score Filter
        bottom_row.addWidget(QLabel("Min Score:"))
        self.txt_min_score = QLineEdit()
        self.txt_min_score.setPlaceholderText("0")
        self.txt_min_score.setStyleSheet("background-color: #202124; border: 1px solid #3D4047; padding: 4px; color: white;")
        self.txt_min_score.textChanged.connect(self.apply_filters)
        bottom_row.addWidget(self.txt_min_score)
        
        # Sorting
        bottom_row.addWidget(QLabel("Sort By:"))
        self.combo_sort = QComboBox()
        self.combo_sort.addItems(["Highest Score", "Highest Confidence", "Highest Momentum", "Highest Volume", "Alphabetical"])
        self.combo_sort.setStyleSheet("background-color: #202124; border: 1px solid #3D4047; padding: 4px; color: white;")
        self.combo_sort.currentTextChanged.connect(self.apply_sorting)
        bottom_row.addWidget(self.combo_sort)
        
        # Auto Refresh Combo
        bottom_row.addWidget(QLabel("Auto-Refresh:"))
        self.combo_refresh = QComboBox()
        self.combo_refresh.addItems(["Off", "10s", "30s", "1m", "5m"])
        self.combo_refresh.setStyleSheet("background-color: #202124; border: 1px solid #3D4047; padding: 4px; color: white;")
        self.combo_refresh.currentTextChanged.connect(self.on_refresh_interval_changed)
        bottom_row.addWidget(self.combo_refresh)
        
        bottom_row.addStretch()
        
        # Action Buttons
        self.btn_scan = QPushButton("Scan")
        self.btn_scan.setStyleSheet(f"background-color: {BTN_BLUE}; color: white; font-weight: bold; padding: 6px 12px;")
        self.btn_scan.clicked.connect(self.run_scan)
        bottom_row.addWidget(self.btn_scan)
        
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setStyleSheet("background-color: #4f5259; color: white; padding: 6px 12px;")
        self.btn_reset.clicked.connect(self.reset_filters)
        bottom_row.addWidget(self.btn_reset)
        
        filter_layout_main.addLayout(top_row)
        filter_layout_main.addLayout(bottom_row)
        
        self.main_layout.addWidget(filter_frame)
        
        # Progress Bar Frame
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"QProgressBar {{ background-color: {CARD_BG}; border-radius: 4px; text-align: center; color: white; }} QProgressBar::chunk {{ background-color: {BTN_BLUE}; }}")
        self.progress_bar.hide()
        self.main_layout.addWidget(self.progress_bar)
        
        # 3. Scanner Statistics Panel
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 8px; border: 1px solid #3D4047;")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(15, 10, 15, 10)
        
        self.lbl_stat_total = QLabel("Total Symbols: --")
        self.lbl_stat_buy = QLabel("BUY: --")
        self.lbl_stat_watch = QLabel("WATCH: --")
        self.lbl_stat_sell = QLabel("SELL: --")
        self.lbl_stat_avg_score = QLabel("Avg Score: --")
        self.lbl_stat_exec_time = QLabel("Exec Time: --")
        
        for lbl in [self.lbl_stat_total, self.lbl_stat_buy, self.lbl_stat_watch, self.lbl_stat_sell, self.lbl_stat_avg_score, self.lbl_stat_exec_time]:
            lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
            stats_layout.addWidget(lbl)
            stats_layout.addStretch()
            
        self.main_layout.addWidget(stats_frame)
        
        # 4. Content Area (Table + Side Panel)
        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        
        # Scanner Results Table
        self.table = ScalpingResultsTable()
        self.table.cellDoubleClicked.connect(self._handle_double_click)
        self.content_layout.addWidget(self.table)
        self.main_layout.addLayout(self.content_layout)
        self.lbl_placeholder = QLabel("No Scan Performed", self.table)
        self.lbl_placeholder.setStyleSheet("font-size: 16px; color: #888; font-weight: bold; background-color: transparent;")
        self.lbl_placeholder.setAlignment(Qt.AlignCenter)
        
        # 5. Export Bar
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        self.btn_export_csv = QPushButton("Export CSV")
        self.btn_export_csv.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 6px 12px;")
        self.btn_export_csv.clicked.connect(self.export_csv)
        self.btn_export_csv.setEnabled(False)
        export_layout.addWidget(self.btn_export_csv)
        
        self.btn_export_excel = QPushButton("Export Excel")
        self.btn_export_excel.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 6px 12px;")
        self.btn_export_excel.clicked.connect(self.export_excel)
        self.btn_export_excel.setEnabled(False)
        export_layout.addWidget(self.btn_export_excel)
        
        self.btn_export_json = QPushButton("Export JSON")
        self.btn_export_json.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold; padding: 6px 12px;")
        self.btn_export_json.clicked.connect(self.export_json)
        self.btn_export_json.setEnabled(False)
        export_layout.addWidget(self.btn_export_json)
        
        self.main_layout.addLayout(export_layout)
        
        self._update_placeholder_position()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_placeholder_position()
        
    def _update_placeholder_position(self):
        if hasattr(self, 'lbl_placeholder') and self.lbl_placeholder:
            try:
                geom = self.content_layout.geometry()
                if geom.width() > 0:
                    self.lbl_placeholder.setGeometry(geom)
                else:
                    self.lbl_placeholder.setGeometry(self.rect())
            except:
                self.lbl_placeholder.setGeometry(self.rect())
            
    def run_scan(self):
        if self.worker and self.worker.isRunning():
            return
            
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("Scanning...")
        self.lbl_placeholder.setText("Scanning Market Tickers...")
        self.lbl_placeholder.show()
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
        self.table.setRowCount(0)
        self.start_time = time.time()
        
        self.worker = ScalpingScanWorker(self.service, "5m") # Default timeframe 5m
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.results_ready.connect(self.on_scan_completed)
        self.worker.start()
        
    def on_scan_completed(self, results):
        self.scan_results = results
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("Scan")
        self.progress_bar.hide()
        
        if not self.scan_results:
            self.lbl_placeholder.setText(
                "Unable to retrieve market data.\n\n"
                "Possible reasons:\n"
                "• Market Closed\n"
                "• API Timeout\n"
                "• Network Error\n"
                "• Data Provider Unavailable\n\n"
                "Click Scan to retry."
            )
            self.lbl_placeholder.show()
            self.btn_export_csv.setEnabled(False)
            self.btn_export_excel.setEnabled(False)
            self.btn_export_json.setEnabled(False)
            
            self.lbl_stat_total.setText("Total Symbols: 0")
            self.lbl_stat_buy.setText("BUY: 0")
            self.lbl_stat_watch.setText("WATCH: 0")
            self.lbl_stat_sell.setText("SELL: 0")
            self.lbl_stat_avg_score.setText("Avg Score: N/A")
            self.lbl_stat_exec_time.setText("Exec Time: 0 ms")
            return
            
        self.lbl_placeholder.hide()
        self.btn_export_csv.setEnabled(True)
        self.btn_export_excel.setEnabled(True)
        self.btn_export_json.setEnabled(True)
        
        # Apply Sorting first
        self.apply_sorting()
        
    def _populate_table(self, results):
        self.table.populate(results)
        
        # Update Statste Stats
        total = len(self.scan_results)
        buys = sum(1 for x in self.scan_results if "BUY" in str(x.get("Signal", "")))
        sells = sum(1 for x in self.scan_results if "SELL" in str(x.get("Signal", "")))
        watches = sum(1 for x in self.scan_results if "WATCH" in str(x.get("Signal", "")))
        avg_score = round(sum(int(x.get("Score", 50)) for x in self.scan_results) / total, 1) if total > 0 else 0.0
        exec_t = time.time() - self.start_time if hasattr(self, 'start_time') else 0.0
        
        self.lbl_stat_total.setText(f"Total Symbols: {total}")
        self.lbl_stat_buy.setText(f"BUY: {buys}")
        self.lbl_stat_watch.setText(f"WATCH: {watches}")
        self.lbl_stat_sell.setText(f"SELL: {sells}")
        self.lbl_stat_avg_score.setText(f"Avg Score: {avg_score}")
        self.lbl_stat_exec_time.setText(f"Exec Time: {exec_t:.2f}s")
        
        self.apply_filters()

    def reset_filters(self):
        self.combo_index.setCurrentIndex(0)
        self.combo_exchange.setCurrentIndex(0)
        self.combo_sector.setCurrentIndex(0)
        self.combo_signal.setCurrentIndex(0)
        self.combo_sort.setCurrentIndex(0)
        self.combo_refresh.setCurrentIndex(0)
        self.txt_min_vol.clear()
        self.txt_min_price.clear()
        self.txt_max_price.clear()
        self.txt_min_score.clear()
        self.apply_filters()

    def apply_filters(self):
        sector = self.combo_sector.currentText()
        signal_type = self.combo_signal.currentText()
        
        try: min_price = float(self.txt_min_price.text()) if self.txt_min_price.text() else 0.0
        except: min_price = 0.0
        
        try: max_price = float(self.txt_max_price.text()) if self.txt_max_price.text() else float('inf')
        except: max_price = float('inf')
        
        try: min_score = int(self.txt_min_score.text()) if self.txt_min_score.text() else 0
        except: min_score = 0
        
        try: min_vol = float(self.txt_min_vol.text()) if self.txt_min_vol.text() else 0.0
        except: min_vol = 0.0
        
        visible_row_count = 0
        for row in range(self.table.rowCount()):
            sec_item = self.table.item(row, 2)
            ltp_item = self.table.item(row, 3)
            sig_item = self.table.item(row, 4)
            score_item = self.table.item(row, 5)
            vol_item = self.table.item(row, 11)
            
            row_sector = sec_item.text() if sec_item else ""
            try: row_ltp = float(ltp_item.text()) if ltp_item else 0.0
            except: row_ltp = 0.0
            row_sig = sig_item.text() if sig_item else ""
            try: row_score = int(score_item.text()) if score_item else 0
            except: row_score = 0
            try: row_vol = float(vol_item.text()) if vol_item else 0.0
            except: row_vol = 0.0
            
            match_sector = (sector == "All" or sector in row_sector)
            match_signal = (signal_type == "All" or row_sig == signal_type)
            match_price = (min_price <= row_ltp <= max_price)
            match_score = (row_score >= min_score)
            match_vol = (row_vol >= min_vol)
            
            hide_row = not (match_sector and match_signal and match_price and match_score and match_vol)
            self.table.setRowHidden(row, hide_row)
            if not hide_row:
                visible_row_count += 1
                
        if self.table.rowCount() > 0 and visible_row_count == 0:
            self.lbl_placeholder.setText("No Matches for Filters")
            self.lbl_placeholder.show()
        elif self.table.rowCount() == 0:
            self.lbl_placeholder.setText("No Scan Performed")
            self.lbl_placeholder.show()
        else:
            self.lbl_placeholder.hide()

    def apply_sorting(self):
        sort_by = self.combo_sort.currentText()
        if not self.scan_results:
            return
            
        if sort_by == "Highest Score":
            self.scan_results.sort(key=lambda x: x.get("Score", 0), reverse=True)
        elif sort_by == "Highest Confidence":
            self.scan_results.sort(key=lambda x: x.get("Confidence", 0.0), reverse=True)
        elif sort_by == "Highest Momentum":
            self.scan_results.sort(key=lambda x: x.get("Momentum", ""), reverse=True)
        elif sort_by == "Highest Volume":
            self.scan_results.sort(key=lambda x: x.get("Volume", 0), reverse=True)
        elif sort_by == "Alphabetical":
            self.scan_results.sort(key=lambda x: x.get("Symbol", ""))
            
        self.populate_table()

    def on_refresh_interval_changed(self, text):
        self.refresh_timer.stop()
        if text == "10s":
            self.refresh_timer.start(10000)
        elif text == "30s":
            self.refresh_timer.start(30000)
        elif text == "1m":
            self.refresh_timer.start(60000)
        elif text == "5m":
            self.refresh_timer.start(300000)

    def export_csv(self):
        filepath = "exports/scalping_scan_results.csv"
        self.service.export_csv(self.scan_results, filepath)

    def export_excel(self):
        filepath = "exports/scalping_scan_results.xlsx"
        self.service.export_excel(self.scan_results, filepath)

    def export_json(self):
        filepath = "exports/scalping_scan_results.json"
        self.service.export_json(self.scan_results, filepath)
        
    def _handle_double_click(self, row, col):
        # Removed automatic navigation to Charts as per UI Behavior Fix rules
        pass

# Define TradingModeScanner alias for main window integration compatibility
TradingModeScanner = ScalpingScannerPage
