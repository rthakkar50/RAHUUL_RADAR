from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QFrame,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QCompleter,
    QTabWidget, QSplitter, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QBrush
from ui.widgets.cards import BestTradeCard, ScanStatsCard
from datetime import datetime, time as dtime
from config.config import AppConfig
import os


def get_market_status():
    now = datetime.now().time()
    if dtime(9, 0) <= now < dtime(9, 15):
        return "🟡 Market Status : PRE-OPEN"
    elif dtime(9, 15) <= now < dtime(15, 30):
        return "🟢 Market Status : OPEN"
    else:
        return "🔴 Market Status : CLOSED"


def get_option_window_status():
    """Returns time window status for option buying."""
    now = datetime.now().time()
    windows = [
        (dtime(9, 20),  dtime(10, 30), "Morning Window"),
        (dtime(14, 0),  dtime(14, 45), "Afternoon Window"),
    ]
    for start, end, label in windows:
        if start <= now <= end:
            return f"✅ Best Time ({label})", "#4CAF50"
    return "⚠️ Outside Optimal Window", "#FF9800"



from PySide6.QtCore import QThread, Signal

class RankingScanThread(QThread):
    progress = Signal(str, int)
    finished_scan = Signal(list, list, list, dict) # Top Buys, Top Sells, Top Watch, Stats
    
    def __init__(self):
        super().__init__()
        from strategy.ranking_engine import RankingEngine
        from market.yahoo_provider import YahooFinanceProvider
        self.ranking_engine = RankingEngine()
        self.yf_provider = YahooFinanceProvider()
        self.yf_provider.connect()
        
    def run(self):
        try:
            from market.universe import FNO_UNIVERSE
            symbols = [item["symbol"] for item in FNO_UNIVERSE][:50]
            total = len(symbols)
            
            all_results = []
            stats = {"Total": total, "Processed": 0, "Rejected": 0}
            
            import time
            start_time = time.time()
            
            for idx, symbol in enumerate(symbols):
                try:
                    ohlcv_1d = self.yf_provider.get_ohlcv(symbol, "1d", "90d")
                    ohlcv_1wk = self.yf_provider.get_ohlcv(symbol, "1wk", "1y")
                    
                    if not ohlcv_1d or not ohlcv_1wk:
                        stats["Rejected"] += 1
                        continue
                        
                    res = self.ranking_engine.evaluate(symbol, ohlcv_1d, ohlcv_1wk)
                    
                    if res["status"] == "RANKED":
                        all_results.append(res)
                        stats["Processed"] += 1
                    else:
                        stats["Rejected"] += 1
                except Exception:
                    stats["Rejected"] += 1
                    
                percent = int(((idx + 1) / total) * 100)
                elapsed = time.time() - start_time
                speed = (idx + 1) / elapsed if elapsed > 0 else 0
                eta = int((total - (idx + 1)) / speed) if speed > 0 else 0
                
                self.progress.emit(f"Scanning... {idx+1} / {total} | ETA: {eta}s", percent)
                
            all_results.sort(key=lambda x: x["score"], reverse=True)
            
            top_buys = [r for r in all_results if r["direction"] == "BULLISH"][:10]
            top_sells = [r for r in all_results if r["direction"] == "BEARISH"][:10]
            
            assigned = {r["symbol"] for r in top_buys + top_sells}
            top_watch = [r for r in all_results if r["symbol"] not in assigned][:10]
            
            self.finished_scan.emit(top_buys, top_sells, top_watch, stats)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Ranking Scan Error: {e}")
            self.finished_scan.emit([], [], [], {})


class FnoScannerScreen(QWidget):
    navigate_to_chart = Signal(str)
    add_to_watchlist = Signal(str)

    def __init__(self):
        super().__init__()
        self.scanner_status_lbl = None
        self.config = AppConfig()
        self.config.load()
        
        self.all_results = []
        self.detail_map = {}

        self.auto_scan_timer = QTimer(self)
        self.auto_scan_timer.timeout.connect(self.start_scan)
        self.is_auto_scan_active = False

        # Refresh time badge every 60 seconds
        self.time_refresh_timer = QTimer(self)
        self.time_refresh_timer.timeout.connect(self._refresh_time_badge)
        self.time_refresh_timer.start(60000)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ── Toolbar Row ─────────────────────────────────────────────────────────
        toolbar_layout = QHBoxLayout()
        
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(["Intraday", "Swing", "Scalp"])
        
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItems(["NSE F&O", "NSE Equity"])
        
        self.tf_combo = QComboBox()
        self.tf_combo.addItems(["1d", "1wk", "15m", "5m"])
        
        self.btn_auto_scan = QPushButton("Auto Scan: OFF")
        self.btn_auto_scan.setCheckable(True)
        self.btn_auto_scan.clicked.connect(self.toggle_auto_scan)
        
        self.btn_scan = QPushButton("⚡ Scan")
        self.btn_scan.setStyleSheet("background-color: #238636; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px;")
        self.btn_scan.clicked.connect(self.start_scan)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search Symbol...")
        self.search_box.setFixedWidth(150)
        self.search_box.textChanged.connect(self.apply_filters)
        
        self.sector_combo = QComboBox()
        self.sector_combo.addItems(["All Sectors", "IT", "BANK", "AUTO", "PHARMA"])
        self.sector_combo.currentTextChanged.connect(self.apply_filters)
        
        self.min_score_combo = QComboBox()
        self.min_score_combo.addItems(["Score: All", "Score > 80", "Score > 70"])
        self.min_score_combo.currentTextChanged.connect(self.apply_filters)
        
        toolbar_layout.addWidget(self.profile_combo)
        toolbar_layout.addWidget(self.exchange_combo)
        toolbar_layout.addWidget(self.tf_combo)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.sector_combo)
        toolbar_layout.addWidget(self.min_score_combo)
        toolbar_layout.addWidget(self.search_box)
        toolbar_layout.addWidget(self.btn_auto_scan)
        toolbar_layout.addWidget(self.btn_scan)
        
        layout.addLayout(toolbar_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # ── Main Splitter ─────────────────────────────────────────────────────
        from PySide6.QtWidgets import QSplitter, QTabWidget, QFormLayout
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Tabs
        self.tabs = QTabWidget()
        
        self.buy_table = self.create_table()
        self.watch_table = self.create_table()
        self.sell_table = self.create_table()
        
        self.tabs.addTab(self.buy_table, "🟢 BUY")
        self.tabs.addTab(self.watch_table, "🟡 WATCH")
        self.tabs.addTab(self.sell_table, "🔴 SELL")
        
        self.buy_table.itemSelectionChanged.connect(lambda: self.on_row_selected(self.buy_table))
        self.watch_table.itemSelectionChanged.connect(lambda: self.on_row_selected(self.watch_table))
        self.sell_table.itemSelectionChanged.connect(lambda: self.on_row_selected(self.sell_table))
        
        splitter.addWidget(self.tabs)
        
        # Right: Side Panel
        self.side_panel = QFrame()
        self.side_panel.setFixedWidth(300)
        self.side_panel.setStyleSheet("background-color: #161B22; border-radius: 8px; border: 1px solid #30363D;")
        panel_layout = QVBoxLayout(self.side_panel)
        
        self.sp_symbol = QLabel("Select a stock to view details.")
        self.sp_symbol.setStyleSheet("font-size: 14px; color: #8B949E; font-style: italic;")
        
        form_layout = QFormLayout()
        self.sp_company = QLabel("--")
        self.sp_signal = QLabel("--")
        self.sp_trend = QLabel("--")
        self.sp_momentum = QLabel("--")
        self.sp_volume = QLabel("--")
        self.sp_vwap = QLabel("--")
        self.sp_ict = QLabel("--")
        self.sp_entry = QLabel("--")
        self.sp_sl = QLabel("--")
        self.sp_tgt1 = QLabel("--")
        self.sp_tgt2 = QLabel("--")
        self.sp_conf = QLabel("--")
        
        form_layout.addRow("Company:", self.sp_company)
        form_layout.addRow("Signal:", self.sp_signal)
        form_layout.addRow("Trend:", self.sp_trend)
        form_layout.addRow("Momentum:", self.sp_momentum)
        form_layout.addRow("Volume:", self.sp_volume)
        form_layout.addRow("VWAP:", self.sp_vwap)
        form_layout.addRow("ICT:", self.sp_ict)
        form_layout.addRow("Entry:", self.sp_entry)
        form_layout.addRow("SL:", self.sp_sl)
        form_layout.addRow("Target 1:", self.sp_tgt1)
        form_layout.addRow("Target 2:", self.sp_tgt2)
        form_layout.addRow("Confidence:", self.sp_conf)
        
        self.sp_reasons = QLabel("--")
        self.sp_reasons.setWordWrap(True)
        self.sp_reasons.setStyleSheet("color: #8B949E; margin-top: 10px;")
        
        
        splitter.addWidget(self.side_panel)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        
        # Hide the form in the side panel until a stock is selected
        self.form_widget = QWidget()
        self.form_widget.setLayout(form_layout)
        panel_layout.insertWidget(1, self.form_widget)
        self.form_widget.hide()
        self.sp_reasons.hide()
        self.reasons_title_lbl = QLabel("Reasons:")
        self.reasons_title_lbl.hide()
        panel_layout.insertWidget(2, self.reasons_title_lbl)
        
        layout.addWidget(splitter, stretch=9)
        self.scanner = None
        
    def create_table(self):
        from PySide6.QtWidgets import QTableWidget, QHeaderView, QAbstractItemView
        table = QTableWidget()
        table.setColumnCount(11) # Hide Price, Change, Volume entirely for now
        table.setHorizontalHeaderLabels([
            "Rank", "Symbol", "Sector", "Signal", "Grade", "Score", "Confidence", 
            "Entry", "SL", "Target", "RR"
        ])
        header_view = table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.Interactive)
        header_view.setDefaultSectionSize(90)
        header_view.resizeSection(0, 45) # Rank
        header_view.setSectionResizeMode(1, QHeaderView.Stretch) # Symbol stretches
        table.setSortingEnabled(True)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        return table

    def apply_filters(self):
        search_text = self.search_box.text().lower()
        sector_filter = self.sector_combo.currentText()
        min_score_filter = self.min_score_combo.currentText()
        
        min_score = 0
        if "80" in min_score_filter: min_score = 80
        elif "70" in min_score_filter: min_score = 70
        
        for table in [self.buy_table, self.sell_table, self.watch_table]:
            for row in range(table.rowCount()):
                match = True
                
                sym_item = table.item(row, 1) # Symbol
                if sym_item and search_text and search_text not in sym_item.text().lower():
                    match = False
                    
                sector_item = table.item(row, 2)
                if sector_item and sector_filter != "All Sectors" and sector_item.text() != sector_filter:
                    match = False
                    
                score_item = table.item(row, 5)
                if score_item and float(score_item.text()) < min_score:
                    match = False
                        
                table.setRowHidden(row, not match)

    def on_row_selected(self, table):
        items = table.selectedItems()
        if not items:
            return
            
        row = items[0].row()
        symbol = table.item(row, 1).text() if table.item(row, 1) else ""
        
        # Find raw dict in all_results
        res = next((r for r in self.all_results if r["symbol"] == symbol), None)
        if not res: return
        
        self.sp_symbol.setText(symbol)
        self.sp_symbol.setStyleSheet("font-size: 18px; font-weight: bold; color: #58A6FF; font-style: normal;")
        self.form_widget.show()
        self.sp_reasons.show()
        self.reasons_title_lbl.show()
        
        self.sp_company.setText(res.get("company_name", res.get("Symbol", "Unknown")))
        self.sp_signal.setText(res.get("direction", "WAIT"))
        self.sp_trend.setText("Bullish" if "Bullish" in str(res.get("reason", "")) else "Unknown")
        self.sp_momentum.setText("Strong" if res.get("score", 0) > 60 else "Weak")
        self.sp_volume.setText(res.get("volume", "--"))
        self.sp_vwap.setText("Active" if "VWAP" in str(res.get("reason", "")) else "--")
        self.sp_ict.setText("Sweep" if "sweep" in str(res.get("reason", "")).lower() else "--")
        
        self.sp_entry.setText(str(res.get("entry", 0.0)))
        self.sp_sl.setText(str(res.get("sl", 0.0)))
        self.sp_tgt1.setText(str(res.get("target1", 0.0)))
        self.sp_tgt2.setText(str(res.get("target2", 0.0)))
        self.sp_conf.setText(f"{res.get('confidence', 0)}%")
        self.sp_reasons.setText(res.get("reason", "--"))

    # ── Badge helpers ──────────────────────────────────────────────────────────
    def _refresh_vix_badge(self):
        """Fetches India VIX and updates the badge label."""
        try:
            import yfinance as yf
            ticker = yf.Ticker("^INDIAVIX")
            hist = ticker.history(period="2d", interval="1d")
            if not hist.empty:
                vix = float(hist["Close"].iloc[-1])
                if vix > 20:
                    color, tag = "#F44336", "⛔ DANGER"
                elif vix > 14:
                    color, tag = "#FF9800", "⚠️ Elevated"
                else:
                    color, tag = "#4CAF50", "✅ Safe"
                self.vix_lbl.setText(f"{vix:.2f}  {tag}")
                self.vix_lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")
            else:
                self.vix_lbl.setText("Unavailable")
        except Exception:
            self.vix_lbl.setText("Unavailable")

    def _refresh_time_badge(self):
        """Refreshes the time window badge."""
        win_text, win_color = get_option_window_status()
        if hasattr(self, 'time_window_lbl'):
            self.time_window_lbl.setText(win_text)
            self.time_window_lbl.setStyleSheet(f"color: {win_color}; font-weight: bold; font-size: 12px;")

    # ── Scan controls ──────────────────────────────────────────────────────────
    def toggle_auto_scan(self):
        self.is_auto_scan_active = not self.is_auto_scan_active
        if self.is_auto_scan_active:
            self.btn_auto_scan.setText("Auto Scan: ON")
            self.btn_auto_scan.setStyleSheet(
                "background-color: #4CAF50; color: white; font-weight: bold; "
                "border: none; padding: 10px 16px; border-radius: 4px;"
            )
            self.btn_scan.setEnabled(False)
            interval_ms = self.config.scan_interval * 1000
            self.auto_scan_timer.start(interval_ms)
            self.start_scan()
        else:
            self.btn_auto_scan.setText("Auto Scan: OFF")
            self.btn_auto_scan.setStyleSheet(
                "background-color: #3D4047; color: white; font-weight: bold; "
                "border: none; padding: 10px 16px; border-radius: 4px;"
            )
            self.btn_scan.setEnabled(True)
            self.auto_scan_timer.stop()
            if not (self.scanner and self.scanner.isRunning()):
                pass

    def start_scan(self):
        if self.scanner and self.scanner.isRunning():
            return

        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("Scanning... 0%")

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Always OPTIONS mode — 5m data, VIX + Time + Volume filters active
        self.scanner = RankingScanThread()
        self.scanner.progress.connect(self.update_progress)
        self.scanner.finished_scan.connect(self.scan_finished)
        self.scanner.start()

    def update_progress(self, text, val):
        self.btn_scan.setText(text)
        self.progress_bar.setValue(val)

    def scan_finished(self, top_buys, top_sells, top_watch, stats):
        self.btn_scan.setEnabled(not self.is_auto_scan_active)
        self.btn_scan.setText("⚡ Scan Now")

        self.progress_bar.hide()
        
        self.all_results = top_buys + top_watch + top_sells  # Store for side panel
        
        self.buy_table.setRowCount(0)
        self.sell_table.setRowCount(0)
        self.watch_table.setRowCount(0)
        
        self.tabs.setTabText(0, f"🟢 BUY ({len(top_buys)})")
        self.tabs.setTabText(1, f"🟡 WATCH ({len(top_watch)})")
        self.tabs.setTabText(2, f"🔴 SELL ({len(top_sells)})")
        
        self.populate_table(self.buy_table, top_buys, "#00C853")
        self.populate_table(self.sell_table, top_sells, "#FF3D00")
        self.populate_table(self.watch_table, top_watch, "#FFC107")

    def _clean_reasons(self, raw_reason: str) -> str:
        if not raw_reason: return ""
        # The engine produces things like "Trend aligned with direction + Momentum aligned (5/20) + High Relative Volume expansion"
        # We need to map these to simple clean UI strings. Max 3.
        reasons = []
        raw_reason = raw_reason.lower()
        if "trend aligned" in raw_reason or "bullish" in raw_reason or "bearish" in raw_reason:
            reasons.append("Trend: Bullish" if "bullish" in raw_reason else "Trend: Bearish" if "bearish" in raw_reason else "Trend: Aligned")
        if "momentum aligned" in raw_reason or "strong" in raw_reason:
            reasons.append("Momentum: Strong")
        if "high" in raw_reason and "volume" in raw_reason:
            reasons.append("Volume: High")
        if "vwap" in raw_reason and "respect" in raw_reason:
            reasons.append("VWAP: Above" if "bullish" in raw_reason else "VWAP: Below")
        if "fvg" in raw_reason or "liquidity sweep" in raw_reason:
            reasons.append("ICT: Sweep/FVG")
        
        # Fallbacks if we didn't get enough
        if len(reasons) < 3 and "volume expansion" in raw_reason:
            reasons.append("Volume: Medium")
        if len(reasons) == 0:
            reasons = ["Trend: Neutral", "Momentum: Medium", "Volume: Low"]
        return " | ".join(reasons[:2])

    def populate_table(self, table, data_list, action_color):
        for row, res in enumerate(data_list):
            table.insertRow(row)
            
            direction = res.get("direction", "WAIT")
            symbol = str(res.get("symbol", res.get("Symbol", "")))
            score = float(res.get("score", 0))
            
            entry_val = float(res.get("entry", 0.0))
            sl_val = float(res.get("sl", 0.0))
            tgt_val = float(res.get("target1", 0.0))
            
            e_str = f"{entry_val:.2f}" if entry_val > 0 else "--"
            sl_str = f"{sl_val:.2f}" if sl_val > 0 else "--"
            t_str = f"{tgt_val:.2f}" if tgt_val > 0 else "--"
            rr_str = "1:2.0+" if entry_val > 0 else "--"
            
            if score >= 90: grade = "★★★★★ Elite"
            elif score >= 80: grade = "★★★★ Strong"
            elif score >= 70: grade = "★★★ Good"
            elif score >= 60: grade = "★★ Watch"
            else: grade = "★ Weak"
            
            items = [
                f"#{row+1}",
                symbol,
                res.get("sector", "FNO"), # Sector
                direction,
                grade,
                str(score),
                f"{res.get('confidence', 0)}%",
                e_str,
                sl_str,
                t_str,
                rr_str
            ]
            
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                # Entry, SL, Target, RR, Last Price, Change %, Volume right aligned
                if col >= 7:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                # Colors
                if col == 3: # Signal
                    item.setForeground(QColor(action_color))
                    font = item.font(); font.setBold(True); item.setFont(font)
                elif col == 4 or col == 5: # Grade / Score
                    font = item.font(); font.setBold(True); item.setFont(font)
                    if score >= 80: item.setForeground(QColor("#00C853")) 
                    elif score >= 70: item.setForeground(QColor("#2EA043"))
                    elif score >= 60: item.setForeground(QColor("#FFC107"))
                    else: item.setForeground(QColor("#8B949E"))
                elif col == 6: # Confidence
                    conf = float(res.get('confidence', 0))
                    if conf >= 80: item.setForeground(QColor("#00C853"))
                    elif conf >= 60: item.setForeground(QColor("#FFC107"))
                    else: item.setForeground(QColor("#FF3D00"))
                    
                table.setItem(row, col, item)

    def export_csv(self):
        import csv
        from datetime import datetime
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        
        default_name = f"swing_scan_{datetime.now().strftime('%d-%b-%Y')}.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Export Scanner Results", default_name, "CSV Files (*.csv)")
        
        if not path:
            return
            
        try:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                headers = ["Rank", "Symbol", "Sector", "Signal", "Score", "Confidence", "Entry", "SL", "Target", "RR", "Reason"]
                writer.writerow(headers)
                
                # Combine tables
                for table in [self.buy_table, self.sell_table, self.watch_table]:
                    for row in range(table.rowCount()):
                        row_data = []
                        # Skip column 0 which is the Star icon
                        for col in range(1, 12):
                            item = table.item(row, col)
                            row_data.append(item.text() if item else "")
                        if row_data:
                            writer.writerow(row_data)
            
            QMessageBox.information(self, "Success", f"Scan exported to:\\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export CSV:\\n{str(e)}")

    def _add_to_watchlist(self, symbol: str):
        try:
            from ui.watchlist import load_watchlist, save_watchlist
            wl = load_watchlist()
            if symbol not in wl:
                wl.append(symbol)
                save_watchlist(wl)
        except Exception as e:
            print("Watchlist add error:", e)
