from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QComboBox, QLineEdit, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QFrame, QSplitter,
                               QAbstractItemView)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QBrush, QColor
from ui.styles import BG_COLOR, CARD_BG, BTN_BLUE, COLOR_BUY, COLOR_WATCH, COLOR_SELL
from application.swing_scanner_service import SwingScannerService
from ui.widgets.stock_analysis_panel import StockAnalysisPanel
from ui.widgets.quick_action_toolbar import QuickActionToolbar
from ui.widgets.scanner_results_table import ScannerResultsTable
from application.scanner_toolbar_service import ScannerToolbarService
import os
import logging
import time

logger = logging.getLogger(__name__)

from PySide6.QtCore import QThread, Signal

class SwingScannerWorker(QThread):
    finished = Signal(dict)
    progress = Signal(int)
    
    def __init__(self, service):
        super().__init__()
        self.service = service
        
    def run(self):
        try:
            results = self.service.execute_swing_scan(progress_callback=self.progress.emit)
            self.finished.emit(results)
        except Exception as e:
            import traceback
            logger.error(f"Error in SwingScannerWorker: {e}")
            logger.error(traceback.format_exc())
            self.finished.emit({})

class SwingScannerPage(QWidget):
    navigate_to_chart = Signal(str)
    scan_completed_stats = Signal(dict)
    
    def __init__(self, mode_name="Swing", engine=None):
        super().__init__()
        self.service = SwingScannerService()
        self.scan_results = []
        self._init_ui()
        
    def _init_ui(self):
        self.scanner_widget = QWidget()
        self.main_layout = QVBoxLayout(self.scanner_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scanner_widget)
        
        # 1. Header
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("Swing Scanner")
        self.lbl_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header_layout.addWidget(self.lbl_title)
        
        header_layout.addStretch()
        
        # Exchange Dropdown in Header
        lbl_ex = QLabel("Exchange:")
        lbl_ex.setStyleSheet("color: #888; font-weight: bold;")
        header_layout.addWidget(lbl_ex)
        self.combo_exchange = QComboBox()
        self.combo_exchange.addItems(["NSE", "BSE"])
        self.combo_exchange.setStyleSheet("background-color: #202124; border: 1px solid #3D4047; border-radius: 4px; padding: 4px; color: white; min-width: 80px;")
        header_layout.addWidget(self.combo_exchange)
        
        # Mode Dropdown in Header
        lbl_mode = QLabel("Signal Mode:")
        lbl_mode.setStyleSheet("color: #888; font-weight: bold; margin-left: 10px;")
        header_layout.addWidget(lbl_mode)
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Conservative", "Balanced", "Aggressive"])
        # Select the mode from config
        idx = self.combo_mode.findText(self.service.config.swing_signal_mode)
        if idx >= 0:
            self.combo_mode.setCurrentIndex(idx)
        else:
            self.combo_mode.setCurrentIndex(1) # Default to Balanced
        self.combo_mode.setStyleSheet("background-color: #202124; border: 1px solid #3D4047; border-radius: 4px; padding: 4px; color: white; min-width: 100px;")
        self.combo_mode.currentTextChanged.connect(self._on_mode_changed)
        header_layout.addWidget(self.combo_mode)
        
        from PySide6.QtWidgets import QPushButton
        from PySide6.QtCore import QTimer
        self.btn_auto_scan = QPushButton("Auto Scan: OFF")
        self.btn_auto_scan.setCheckable(True)
        self.btn_auto_scan.setStyleSheet("QPushButton { background-color: #2D2F34; color: white; border-radius: 4px; padding: 4px 10px; font-weight: bold; } QPushButton:checked { background-color: #4CAF50; }")
        self.btn_auto_scan.clicked.connect(self._toggle_auto_scan)
        header_layout.addWidget(self.btn_auto_scan)
        
        self.auto_scan_timer = QTimer(self)
        self.auto_scan_timer.timeout.connect(self.run_scan)
        
        self.main_layout.addLayout(header_layout)
        
        # 2.5 Progress Bar
        from PySide6.QtWidgets import QProgressBar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()
        self.main_layout.addWidget(self.progress_bar)
        
        
        
        # (Removed Best Trades Panel based on user request)
        # 3.7 Quick Action Toolbar
        self.toolbar = QuickActionToolbar()
        self.main_layout.addWidget(self.toolbar)
        self._setup_toolbar_connections()
        
        # 4. Content Area (Splitter: Table + Details Panel)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(2)
        
        # Table Container
        self.table_container = QWidget()
        table_layout = QVBoxLayout(self.table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(5)
        
        # Filter Tabs (BUY / READY / WATCH / SELL)
        self.filter_tabs = QHBoxLayout()
        self.filter_tabs.setSpacing(0)
        self.filter_tabs.setAlignment(Qt.AlignLeft)
        
        self.btn_filter_buy = QPushButton("🟢 BUY (0)")
        self.btn_filter_ready = QPushButton("🟠 READY (0)")
        self.btn_filter_watch = QPushButton("🟡 WATCH (0)")
        self.btn_filter_sell = QPushButton("🔴 SELL (0)")
        
        for btn in [self.btn_filter_buy, self.btn_filter_ready, self.btn_filter_watch, self.btn_filter_sell]:
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background: #1A1C20;
                    color: #888888;
                    padding: 8px 25px;
                    font-weight: bold;
                    font-size: 14px;
                    border: 1px solid #3D4047;
                    border-bottom: none;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                    border-bottom-left-radius: 0px;
                    border-bottom-right-radius: 0px;
                    margin-right: 2px;
                }
                QPushButton:checked {
                    background: #00A3E0;
                    color: white;
                    border: 1px solid #00A3E0;
                    border-bottom: none;
                }
                QPushButton:hover:!checked {
                    background: #2A2C30;
                }
            """)
            self.filter_tabs.addWidget(btn)
            
        self.btn_filter_buy.clicked.connect(lambda: self._set_active_tab("BUY"))
        self.btn_filter_ready.clicked.connect(lambda: self._set_active_tab("READY"))
        self.btn_filter_watch.clicked.connect(lambda: self._set_active_tab("WATCH"))
        self.btn_filter_sell.clicked.connect(lambda: self._set_active_tab("SELL"))
        
        # Default to BUY
        self.active_tab = "BUY"
        self.btn_filter_buy.setChecked(True)
        
        table_layout.addLayout(self.filter_tabs)
        
        # Single Results Table
        self.table = ScannerResultsTable()
        self.table.itemSelectionChanged.connect(self._handle_table_selection)
        self.table.cellDoubleClicked.connect(lambda r, c: self._handle_double_click(r, c, self.table))
        
        table_layout.addWidget(self.table)
        self.splitter.addWidget(self.table_container)
        
        # Right Details Panel
        from ui.widgets.trade_setup_panel import SmartTradeSetupPanel
        self.details_panel = SmartTradeSetupPanel()
        self.details_panel.setMinimumWidth(280)
        self.details_panel.setMaximumWidth(400)
        self.splitter.addWidget(self.details_panel)
        
        self.splitter.setSizes([900, 300])
        self.main_layout.addWidget(self.splitter)
        
        self.analysis_dialog = None
        
        # Placeholder Overlay
        self.lbl_placeholder = QLabel("No Scan Performed", self.table)
        self.lbl_placeholder.setStyleSheet("font-size: 16px; color: #888; font-weight: bold; background-color: transparent;")
        self.lbl_placeholder.setAlignment(Qt.AlignCenter)
        self.lbl_placeholder.hide()
        
        self._update_placeholder_position()
        
    def _on_mode_changed(self, new_mode):
        self.service.config.swing_signal_mode = new_mode
        self.run_scan()

    def _set_active_tab(self, tab_name):
        self.active_tab = tab_name
        self.btn_filter_buy.setChecked(tab_name == "BUY")
        self.btn_filter_ready.setChecked(tab_name == "READY")
        self.btn_filter_watch.setChecked(tab_name == "WATCH")
        self.btn_filter_sell.setChecked(tab_name == "SELL")
        self._on_tab_changed()
        self._apply_toolbar_filters()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_placeholder_position()
        
    def _update_placeholder_position(self):
        if hasattr(self, 'lbl_placeholder') and self.lbl_placeholder:
            self.lbl_placeholder.setGeometry(self.table.rect())
            
    def _on_progress_update(self, percentage):
        self.progress_bar.setValue(percentage)
        self.progress_bar.setFormat(f"Scanning... {percentage}%")

    def run_scan(self):
        logger.info("Entered Function: run_scan() [Event Handler]")
        logger.info("Input: Run Scan Button Click")
        self._scan_start_t = time.time()
        
        self.lbl_placeholder.setText("Scanning Market Tickers...")
        self.lbl_placeholder.show()
        
        # Reset and show progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Initializing Scan...")
        self.progress_bar.show()
        
        # Force GUI refresh
        self.table.setRowCount(0)
        
        # BUG-4 & BUG-13 FIX: (Best Trades Panel removed)
        
        
        
        
        
        
        
                
        self.repaint()
        
        try:
            logger.info("Calling Scanner Service...")
            self.scanner_thread = SwingScannerWorker(self.service)
            self.scanner_thread.finished.connect(self._on_scan_finished)
            self.scanner_thread.progress.connect(self._on_progress_update)
            self.scanner_thread.start()
            
            logger.info(f"Execution Time (run_scan init): {time.time() - self._scan_start_t:.2f}s")
        except Exception as e:
            import traceback
            logger.error(f"Execution stopped at ui/pages/swing_scanner_page.py, run_scan, line 223")
            logger.error(traceback.format_exc())
            raise

    def _on_scan_finished(self, payload):
        logger.info("Entered Function: _on_scan_finished() [Result Table Population]")
        start_t = time.time()
        
        # Handle dict payload from Smart Filter Engine
        if isinstance(payload, dict):
            if "error" in payload:
                self.scan_results = []
                self.progress_bar.hide()
                self.lbl_placeholder.setText(f"Scan Failed:\n{payload['error']}")
                self.lbl_placeholder.show()
                exec_t = time.time() - getattr(self, "_scan_start_t", time.time())
                stats_payload = {"scanned": 0, "universe": 0, "exec_time": exec_t, "errors": 1}
                self.scan_completed_stats.emit(stats_payload)
                self.toolbar.update_status(time.strftime("%H:%M:%S"), exec_t, "FAILED")
                return

            self.scan_results = payload.get("qualified_results", [])
            market_quality = payload.get("market_quality", "N/A")
            total_scanned = payload.get("total_scanned", 0)
            total_universe = payload.get("total_universe", total_scanned)
            rejected_count = payload.get("rejected_count", 0)
            best_trades = payload.get("best_trades", [])
        else:
            self.scan_results = payload if isinstance(payload, list) else []
            market_quality = "N/A"
            total_scanned = len(self.scan_results)
            total_universe = total_scanned
            rejected_count = 0
            best_trades = []
            
        self.progress_bar.hide()
        
        if not self.scan_results:
            if total_universe == 0:
                error_text = "No symbols loaded for Swing Scanner.\nPlease check Universe Configuration."
            elif total_scanned == 0:
                error_text = (
                    "Market data unavailable (Provider failed or Network timeout).\n\n"
                    "Possible reasons:\n"
                    "• Market Closed / Data Missing\n"
                    "• API Timeout / Rate Limit\n"
                    "• Network Error\n\n"
                    "Click Scan to retry."
                )
            else:
                error_text = f"Scan completed: 0 candidates found\n(No valid stocks after filters out of {total_scanned} scanned)"
                
            self.lbl_placeholder.setText(error_text)
            self.lbl_placeholder.show()
            
            exec_t = time.time() - getattr(self, "_scan_start_t", time.time())
            stats_payload = {
                "scanned": total_scanned,
                "universe": total_universe,
                "exec_time": exec_t,
                "errors": max(0, total_universe - total_scanned)
            }
            self.scan_completed_stats.emit(stats_payload)
            self.toolbar.update_status(time.strftime("%H:%M:%S"), exec_t, market_quality)
            logger.info(f"Execution Time (_on_scan_finished empty): {time.time() - start_t:.2f}s")
            return
            
        # Render Best Trades (Removed based on user request)
        # Populate Table
        self.displayed_results = self.scan_results
        ui_start = time.time()
        self._populate_table(self.displayed_results, total_scanned, rejected_count)
        ui_render_t = time.time() - ui_start
        
        exec_t = time.time() - getattr(self, "_scan_start_t", time.time())
        scan_t = max(0, exec_t - ui_render_t)
        self.toolbar.update_status(time.strftime("%H:%M:%S"), exec_t, market_quality)
        
        # Emit stats to main window footer
        stats_payload = {
            "scanned": total_scanned,
            "universe": payload.get("total_universe", total_scanned) if isinstance(payload, dict) else total_scanned,
            "exec_time": exec_t,
            "errors": max(0, payload.get("total_universe", total_scanned) - total_scanned) if isinstance(payload, dict) else 0
        }
        self.scan_completed_stats.emit(stats_payload)
        
        logger.info(f"Output: {len(self.displayed_results)} rows rendered.")
        logger.info(f"Execution Time (Scan): {scan_t:.2f}s | (UI): {ui_render_t:.2f}s | (Total): {exec_t:.2f}s")

    def _populate_table(self, results, total_scanned=0, rejected_count=0):
        # Dynamic Signal Alias Mapping for Backend Compatibility
        for r in results:
            sig = str(r.get("Signal", "")).upper()
            if "BULLISH" in sig: r["Signal"] = "BUY"
            elif "BEARISH" in sig: r["Signal"] = "SELL"
            elif "READY" in sig or "SETUP" in sig: r["Signal"] = "READY"
            
        buy_results = [r for r in results if "BUY" in str(r.get("Signal", "")).upper()]
        ready_results = [r for r in results if "READY" in str(r.get("Signal", "")).upper()]
        watch_results = [r for r in results if "WATCH" == str(r.get("Signal", "")).upper()]
        sell_results = [r for r in results if "SELL" in str(r.get("Signal", "")).upper()]
        
        # Update Tab buttons text with counts
        self.btn_filter_buy.setText(f"🟢 BUY ({len(buy_results)})")
        self.btn_filter_ready.setText(f"🟠 READY ({len(ready_results)})")
        self.btn_filter_watch.setText(f"🟡 WATCH ({len(watch_results)})")
        self.btn_filter_sell.setText(f"🔴 SELL ({len(sell_results)})")
        
        # Filter the single table by the active tab
        if self.active_tab == "BUY":
            active_results = buy_results
        elif self.active_tab == "READY":
            active_results = ready_results
        elif self.active_tab == "WATCH":
            active_results = watch_results
        else:
            active_results = sell_results

        self.table.clearContents()
        self.table.setRowCount(0)
        
        if not active_results:
            self.lbl_placeholder.setText(f"No {self.active_tab} Candidates Found")
            self.lbl_placeholder.show()
        else:
            self.table.populate(active_results)
            self.lbl_placeholder.hide()
            
        # Update Stats (kept in background for completeness if needed by other widgets)
        displayed = len(results)
        avg_score = round(sum(float(x["Score"]) for x in results) / displayed, 1) if displayed > 0 else 0.0
        avg_conf = round(sum(float(x["Confidence"]) for x in results) / displayed, 1) if displayed > 0 else 0.0
        
        # Time and Market are updated in _on_scan_finished via toolbar, but we can set defaults here if needed


    def export_csv(self):
        filepath = "exports/swing_scan_results.csv"
        results = getattr(self, 'displayed_results', self.scan_results)
        self.service.export_csv(results, filepath)

    def export_excel(self):
        filepath = "exports/swing_scan_results.xlsx"
        results = getattr(self, 'displayed_results', self.scan_results)
        self.service.export_excel(results, filepath)

    def export_json(self):
        filepath = "exports/swing_scan_results.json"
        results = getattr(self, 'displayed_results', self.scan_results)
        self.service.export_json(results, filepath)
        
    def _handle_double_click(self, row, col, table=None):
        if table is None:
            table = self.table
            if not table.selectedItems(): return
            row = list(set(item.row() for item in table.selectedItems()))[0]
            
        sym_item = table.item(row, 0)
        if sym_item:
            data = sym_item.data(Qt.UserRole)
            if data:
                from ui.widgets.stock_analysis_panel import StockAnalysisPanel
                if not hasattr(self, 'analysis_dialog') or self.analysis_dialog is None:
                    self.analysis_dialog = StockAnalysisPanel(self)
                self.analysis_dialog.update_data(data)
                self.analysis_dialog.show_panel()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if hasattr(self, 'analysis_dialog') and self.analysis_dialog is not None and self.analysis_dialog.isVisible():
                self.analysis_dialog.hide_panel()
            else:
                self.table.clearSelection()
        elif event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_F:
                self.toolbar.search_input.setFocus()
            elif event.key() == Qt.Key_R:
                self.run_scan()
            elif event.key() == Qt.Key_E:
                self._handle_toolbar_action("export_csv")
            elif event.key() == Qt.Key_C:
                self._handle_toolbar_action("copy_symbol")
            elif event.key() == Qt.Key_Return:
                self._handle_toolbar_action("open_analysis")
        super().keyPressEvent(event)

    def _on_tab_changed(self):
        """Clear selection and details panel when switching tabs (BUG-10)."""
        self.table.clearSelection()
        if hasattr(self, 'details_panel'):
            self.details_panel.update_panel({"error": "Select a row to view trade setup"})
        self.toolbar.lbl_selected.setText("0 Selected")
        for btn in self.toolbar.selection_buttons:
            btn.setEnabled(False)

    def _setup_toolbar_connections(self):
        self.toolbar.action_requested.connect(self._handle_toolbar_action)
        self.toolbar.search_changed.connect(self._apply_toolbar_filters)
        self.toolbar.filter_changed.connect(self._apply_toolbar_filters)
        self.toolbar.sort_changed.connect(self._apply_toolbar_filters)
        
    def _handle_table_selection(self):
        selected_items = self.table.selectedItems()
        self.toolbar.lbl_selected.setText(f"{len(set(i.row() for i in selected_items))} Selected")
        
        # Enable Toolbar Buttons
        has_sel = len(selected_items) > 0
        for btn in self.toolbar.selection_buttons:
            btn.setEnabled(has_sel)
            
        if has_sel:
            # Update Details Panel
            row = list(set(item.row() for item in selected_items))[0]
            sym_item = self.table.item(row, 0)
            if sym_item:
                data = sym_item.data(Qt.UserRole)
                if data:
                    self.details_panel.update_panel(data)
        else:
            self.details_panel.update_panel({"error": "No Selection"})
        
    def _handle_toolbar_action(self, action: str):
        if action == "refresh" or action == "scan":
            self.run_scan()
        elif action == "export_csv":
            self.export_csv()
        elif action == "export_excel":
            self.export_excel()
        elif action == "export_json":
            self.export_json()
        elif action == "copy_symbol":
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt
            symbols = []
            for row in set(item.row() for item in self.table.selectedItems()):
                item_0 = self.table.item(row, 0)
                if item_0:
                    data = item_0.data(Qt.UserRole)
                    if data and "Symbol" in data:
                        symbols.append(data["Symbol"])
            QApplication.clipboard().setText(",".join(symbols))
            logger.info(f"Copied symbols: {symbols}")
        elif action == "open_chart":
            pass
        elif action == "open_analysis":
            rows = set(item.row() for item in self.table.selectedItems())
            if rows:
                self._handle_double_click(list(rows)[0], 0, self.table)
                return
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "No Stock Selected")
                
    def _apply_toolbar_filters(self, _=None):
        if not hasattr(self, 'scan_results') or not self.scan_results:
            return
            
        search_text = self.toolbar.search_input.text().lower()
        sector_filter = self.toolbar.combo_sector.currentText()
        score_filter = self.toolbar.combo_score.currentText()
        
        filtered = self.scan_results
        
        # 1. Search text
        if search_text:
            filtered = [
                r for r in filtered 
                if search_text in r.get("Symbol", "").lower() 
                or search_text in r.get("Company", "").lower() 
                or search_text in r.get("Sector", "").lower()
            ]
            
        # 2. Sector Filter
        if sector_filter and sector_filter != "All Sectors":
            filtered = [r for r in filtered if r.get("Sector", "").upper() == sector_filter.upper()]
            
        # 3. Score Filter
        if score_filter and score_filter != "All Scores":
            if "Elite" in score_filter:
                filtered = [r for r in filtered if float(r.get("Score", 0)) >= 90.0]
            elif "Strong" in score_filter:
                filtered = [r for r in filtered if float(r.get("Score", 0)) >= 80.0]
            elif "Good" in score_filter:
                filtered = [r for r in filtered if float(r.get("Score", 0)) >= 70.0]
                
        self.displayed_results = filtered
        self._populate_table(filtered)
        
    def _toggle_auto_scan(self, checked):
        if checked:
            self.btn_auto_scan.setText("Auto Scan: ON")
            self.auto_scan_timer.start(300000) # 5 minutes
            self.run_scan()
        else:
            self.btn_auto_scan.setText("Auto Scan: OFF")
            self.auto_scan_timer.stop()

# Define TradingModeScanner alias for main window integration compatibility
TradingModeScanner = SwingScannerPage
