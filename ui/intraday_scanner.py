from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QComboBox, QFrame,
    QAbstractItemView, QMenu, QApplication, QSplitter, QLineEdit, QTabWidget
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QColor
import time
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger("IntradayScannerUI")

from strategy.ranking_engine import RankingEngine
from market.yahoo_provider import YahooFinanceProvider
from application.intraday_quality_gate import IntradayQualityGate
from application.market_intelligence import MarketIntelligenceEngine

class IntradayScanThread(QThread):
    progress = Signal(int)
    status = Signal(str)
    finished_scan = Signal(list, list, list, dict) # Top Buys, Top Sells, Top Watch, Stats
    
    def __init__(self, timeframe: str):
        super().__init__()
        self.timeframe = timeframe
        self.ranking_engine = RankingEngine()
        self.yf_provider = YahooFinanceProvider()
        self.yf_provider.connect()
        
    def run(self):
        from market.universe import FNO_UNIVERSE
        symbols = [item["symbol"] for item in FNO_UNIVERSE]
        total = len(symbols)
        
        yf_interval_map = {"1m": "1m", "3m": "1m", "5m": "5m", "15m": "15m"}
        
        all_results = []
        stats = {"Total": total, "Processed": 0, "Rejected": 0, "Rejected_Gate": 0, "Rejected_NoData": 0}
        
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed
        start_time = time.time()
        
        self.status.emit("Evaluating Market Intelligence Layer...")
        mi_engine = MarketIntelligenceEngine(self.yf_provider)
        market_context = mi_engine.evaluate_market_context()
        stats["Market_Regime"] = market_context.get("regime", "Sideways")
        
        self.status.emit(f"Market Regime: {stats['Market_Regime']} | Downloading Market Data...")
        self.yf_provider.pre_cache(symbols, yf_interval_map[self.timeframe], "5d")
        self.yf_provider.pre_cache(symbols, "1d", "90d")
        
        # Parallel Execution
        def process_symbol(sym):
            try:
                o_5m = self.yf_provider.get_ohlcv(sym, yf_interval_map[self.timeframe], "5d")
                o_1d = self.yf_provider.get_ohlcv(sym, "1d", "90d")
                if o_5m is None or o_1d is None: return (sym, None, "REJECTED_NO_DATA")
                res = self.ranking_engine.evaluate(sym, o_5m, o_1d)
                return (sym, res, "SUCCESS")
            except Exception as e:
                return (sym, None, str(e))

        with ThreadPoolExecutor(max_workers=12) as executor:
            future_to_sym = {executor.submit(process_symbol, sym): sym for sym in symbols}
            for idx, future in enumerate(as_completed(future_to_sym)):
                sym, res, status_msg = future.result()
                
                if res and res.get("status") == "RANKED":
                    all_results.append(res)
                    stats["Processed"] += 1
                else:
                    stats["Rejected_NoData"] += 1
                    logger.warning(f"[{sym}] NO DATA: {status_msg}")
                
                percent = int(((idx + 1) / total) * 100)
                elapsed = time.time() - start_time
                speed = (idx + 1) / elapsed if elapsed > 0 else 0
                eta = int((total - (idx + 1)) / speed) if speed > 0 else 0
                
                self.status.emit(f"Scanning... {idx+1} / {total} | {percent}% | ETA: {eta}s")
                self.progress.emit(percent)
            
        self.status.emit("Applying Institutional Quality Gate...")
        
        top_buys = []
        top_sells = []
        top_watch = []
        
        rejections = {}
        for r in all_results:
            # DEBUG LOGGING
            sym = r.get("symbol", "UNKNOWN")
            metrics = r.get("debug_metrics", {})
            vol_val = metrics.get('Volume', 0)
            vol_ma = metrics.get('Vol_MA20', 1)
            rel_vol = round(vol_val / vol_ma, 2) if vol_ma > 0 else 0
            
            logger.info(
                f"[{sym}] EVALUATION PIPELINE: "
                f"Price={metrics.get('Last Price')}, VWAP={metrics.get('VWAP')}, "
                f"EMA20={metrics.get('EMA20')}, ADX={metrics.get('ADX')}, "
                f"ATR={metrics.get('ATR')}, RelVol={rel_vol}x, "
                f"Momentum Score={r.get('engine_breakdown', {}).get('Momentum', {}).get('Score Contribution')}, "
                f"Confidence={r.get('confidence')}, Signal={r.get('direction')}"
            )
            
            passed, signal, custom_score, custom_reasons, rejection_reason = IntradayQualityGate.evaluate(r, market_context)
            if passed:
                r["score"] = custom_score
                r["reason"] = " | ".join(custom_reasons)
                r["_quality_reason"] = "Passed"
                if signal == "BUY":
                    top_buys.append(r)
                elif signal == "SELL":
                    top_sells.append(r)
                elif signal == "WATCH":
                    top_watch.append(r)
            else:
                stats["Rejected_Gate"] += 1
                rejections[rejection_reason] = rejections.get(rejection_reason, 0) + 1
        
        # Log rejection stats for diagnostics
        ui_logger = logging.getLogger("IntradayScannerUI")
        ui_logger.info(f"--- SPRINT-92 Rejection Log ---")
        ui_logger.info(f"Scanned  : {total}")
        ui_logger.info(f"Qualified: {len(top_buys) + len(top_sells) + len(top_watch)}")
        ui_logger.info(f"Rejected (No Data): {stats['Rejected_NoData']}")
        ui_logger.info(f"Rejected (Gate)   : {stats['Rejected_Gate']}")
        ui_logger.info("Rejected Reasons:")
        for reason, count in sorted(rejections.items(), key=lambda x: x[1], reverse=True):
            ui_logger.info(f"  - {reason}: {count}")
        ui_logger.info("-------------------------------")
        
        # Sort each by score descending
        top_buys.sort(key=lambda x: x["score"], reverse=True)
        top_sells.sort(key=lambda x: x["score"], reverse=True)
        top_watch.sort(key=lambda x: x["score"], reverse=True)

        # Auto-promote top candidates to ensure BUY and SELL tables are never empty
        if not top_buys and top_watch:
            bullish_watches = [r for r in top_watch if r.get("direction") == "BULLISH"]
            if bullish_watches:
                top_buys = bullish_watches[:5]
                for r in top_buys:
                    if r in top_watch: top_watch.remove(r)
                    
        if not top_sells and top_watch:
            bearish_watches = [r for r in top_watch if r.get("direction") == "BEARISH"]
            if bearish_watches:
                top_sells = bearish_watches[:5]
                for r in top_sells:
                    if r in top_watch: top_watch.remove(r)
                    
        stats["Qualified"] = len(top_buys) + len(top_sells) + len(top_watch)
        
        self.status.emit("Scan Complete")
        self.finished_scan.emit(top_buys, top_sells, top_watch, stats)


class IntradayScannerPage(QWidget):
    """
    INTRADAY V2: RANKING ENGINE UI
    """
    navigate_to_chart = Signal(str)

    def __init__(self):
        super().__init__()
        self.scan_thread = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header Controls
        # ── Toolbar Row ─────────────────────────────────────────────────────────
        toolbar_layout = QHBoxLayout()
        
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(["Intraday", "Swing", "Scalp"])
        
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItems(["NSE F&O", "NSE Equity"])
        
        self.combo_tf = QComboBox()
        self.combo_tf.addItems(["5m", "15m"])
        
        self.btn_auto_scan = QPushButton("Auto Scan: OFF")
        self.btn_auto_scan.setCheckable(True)
        self.btn_auto_scan.toggled.connect(self.toggle_auto_scan)
        
        self.btn_scan = QPushButton("⚡ Scan")
        self.btn_scan.setStyleSheet("background-color: #238636; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px;")
        self.btn_scan.clicked.connect(self.run_scan_cycle)
        self.scan_thread = None
        self.all_results = []
        self.detail_map = {}
        self.is_auto_scan_active = False

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
        toolbar_layout.addWidget(self.combo_tf)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.sector_combo)
        toolbar_layout.addWidget(self.min_score_combo)
        toolbar_layout.addWidget(self.search_box)
        toolbar_layout.addWidget(self.btn_auto_scan)
        toolbar_layout.addWidget(self.btn_scan)
        
        layout.addLayout(toolbar_layout)

        # Progress & Status
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet("color: #8B949E; font-size: 13px; font-weight: bold;")
        layout.addWidget(self.lbl_status)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.hide()
        layout.addWidget(self.progress)
        
        # Zero Results Message Label
        self.lbl_no_results = QLabel("🔍 No high-quality intraday opportunity found today.")
        self.lbl_no_results.setStyleSheet("color: #8B949E; font-size: 16px; font-weight: bold;")
        self.lbl_no_results.setAlignment(Qt.AlignCenter)
        self.lbl_no_results.hide()
        layout.addWidget(self.lbl_no_results)
        
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
        from ui.widgets.trade_setup_panel import SmartTradeSetupPanel
        self.side_panel = SmartTradeSetupPanel()
        self.side_panel.setFixedWidth(300)
        
        splitter.addWidget(self.side_panel)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        
        layout.addWidget(splitter, stretch=9)
        
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.run_scan_cycle)
        
    def create_table(self):
        from PySide6.QtWidgets import QTableWidget, QHeaderView, QAbstractItemView
        table = QTableWidget()
        table.setColumnCount(12)
        table.setHorizontalHeaderLabels([
            "Rank", "Type", "Symbol", "Sector", "Signal", "Grade", "Score", "Confidence", 
            "Entry", "SL", "Target", "RR"
        ])
        header_view = table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.Interactive)
        header_view.setDefaultSectionSize(85)
        header_view.resizeSection(0, 45) # Rank
        header_view.resizeSection(1, 100) # Type
        header_view.setSectionResizeMode(2, QHeaderView.Stretch) # Symbol
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
        visible_rows = 0
        if "80" in min_score_filter: min_score = 80
        elif "70" in min_score_filter: min_score = 70
        
        for table in [self.buy_table, self.sell_table, self.watch_table]:
            for row in range(table.rowCount()):
                match = True
                
                sym_item = table.item(row, 1)
                if sym_item and search_text and search_text not in sym_item.text().lower():
                    match = False
                    
                sector_item = table.item(row, 2)
                if sector_item and sector_filter != "All Sectors" and sector_item.text() != sector_filter:
                    match = False
                    
                score_item = table.item(row, 5)
                if score_item and float(score_item.text()) < min_score:
                    match = False
                        
                table.setRowHidden(row, not match)
                if match:
                    visible_rows += 1
                    
        ui_logger = logging.getLogger("IntradayScannerUI")
        ui_logger.info(f"Rows visible after filter: {visible_rows}")

    def on_row_selected(self, table):
        items = table.selectedItems()
        if not items:
            return
            
        row = items[0].row()
        symbol = table.item(row, 1).text() if table.item(row, 1) else ""
        
        res = next((r for r in self.all_results if r["symbol"] == symbol), None)
        if not res: return
        
        score = float(res.get("score", 0))
        if score >= 90: grade = "★★★★★ A+"
        elif score >= 80: grade = "★★★★☆ A"
        elif score >= 70: grade = "★★★☆☆ B"
        else: grade = "★☆☆☆☆ Reject"
        
        reasons_list = []
        reason_str = str(res.get("reason", ""))
        if reason_str:
            reasons_list = [r.strip() for r in reason_str.split("|")]
        else:
            reasons_list = ["Standard breakdown logic"]
            
        mapped_data = {
            "Symbol": symbol,
            "Company": res.get("company_name", res.get("Symbol", "Unknown")),
            "Sector": res.get("sector", "FNO"),
            "Signal": res.get("direction", "WAIT"),
            "Trend": "Bullish" if "bullish" in reason_str.lower() else "Bearish" if "bearish" in reason_str.lower() else "Neutral",
            "Momentum": "Strong" if score > 60 else "Weak",
            "Volume": res.get("volume", "--"),
            "Entry": res.get("entry", 0.0),
            "Stop Loss": res.get("sl", 0.0),
            "Target 1": res.get("target1", 0.0),
            "Confidence": res.get("confidence", 0),
            "Trade Grade": grade,
            "Score": score,
            "_why_selected": reasons_list,
            "Risk Reward": "1:2.0+"
        }
        
        self.side_panel.update_panel(mapped_data)
        
    def toggle_auto_scan(self):
        self.is_auto_scan_active = not getattr(self, 'is_auto_scan_active', False)
        if self.is_auto_scan_active:
            self.btn_auto_scan.setText("Auto Scan: ON")
            self.btn_auto_scan.setStyleSheet(
                "background-color: #4CAF50; color: white; font-weight: bold; "
                "border: none; padding: 10px 16px; border-radius: 4px;"
            )
            self.btn_scan.setEnabled(False)
            interval_ms = getattr(self.config, 'scan_interval', 60) * 1000
            self.refresh_timer.start(interval_ms)
            self.run_scan_cycle()
        else:
            self.btn_auto_scan.setText("Auto Scan: OFF")
            self.btn_auto_scan.setStyleSheet(
                "background-color: #3D4047; color: white; font-weight: bold; "
                "border: none; padding: 10px 16px; border-radius: 4px;"
            )
            self.btn_scan.setEnabled(True)
            self.refresh_timer.stop()

    def run_scan_cycle(self):
        if self.scan_thread and self.scan_thread.isRunning():
            return
            
        self.btn_scan.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.buy_table.setRowCount(0)
        self.sell_table.setRowCount(0)
        self.watch_table.setRowCount(0)
        
        tf = self.combo_tf.currentText()
        self.scan_thread = IntradayScanThread(tf)
        self.scan_thread.progress.connect(self.progress.setValue)
        self.scan_thread.status.connect(self.lbl_status.setText)
        self.scan_thread.finished_scan.connect(self.scan_finished)
        
        self.scan_thread.start()
            
    def scan_finished(self, top_buys, top_sells, top_watch, stats):
        
        self.all_results = top_buys + top_sells + top_watch 
        
        self.tabs.setTabText(0, f"🟢 BUY ({len(top_buys)})")
        self.tabs.setTabText(1, f"🟡 WATCH ({len(top_watch)})")
        self.tabs.setTabText(2, f"🔴 SELL ({len(top_sells)})")
        
        self.populate_table(self.buy_table, top_buys, "#00C853")
        self.populate_table(self.sell_table, top_sells, "#FF3D00")
        self.populate_table(self.watch_table, top_watch, "#FFC107")
        self.progress.hide()
        
        # Add debug logging for population
        ui_logger = logging.getLogger("IntradayScannerUI")
        ui_logger.info(f"--- SPRINT-94 Table Population ---")
        ui_logger.info(f"Qualified Count: {len(top_buys) + len(top_sells) + len(top_watch)}")
        ui_logger.info(f"BUY Count: {len(top_buys)}")
        ui_logger.info(f"SELL Count: {len(top_sells)}")
        ui_logger.info(f"WATCH Count: {len(top_watch)}")
        ui_logger.info(f"Rows inserted into BUY table: {self.buy_table.rowCount()}")
        ui_logger.info(f"Rows inserted into SELL table: {self.sell_table.rowCount()}")
        ui_logger.info(f"Rows inserted into WATCH table: {self.watch_table.rowCount()}")
        self.btn_scan.setEnabled(not self.is_auto_scan_active)
        self.btn_scan.setText("⚡ Scan Now")
        
        processed = stats.get("Processed", 0)
        rejected_nodata = stats.get("Rejected_NoData", 0)
        rejected_gate = stats.get("Rejected_Gate", 0)
        total = stats.get("Total", 0)
        qualified = stats.get("Qualified", 0)
        regime = stats.get("Market_Regime", "Unknown")
        self.lbl_status.setText(f"Regime: {regime} | Scanned: {total} | Ranked: {processed} | Qualified: {qualified} | Rejected (No Data): {rejected_nodata} | Rejected (Gate): {rejected_gate}")
        
        if qualified == 0:
            self.lbl_no_results.show()
            self.tabs.hide()
            self.side_panel.hide()
        else:
            self.lbl_no_results.hide()
            self.tabs.show()
            self.side_panel.show()
        
    def _clean_reasons(self, raw_reason: str) -> str:
        if not raw_reason: return ""
        reasons = [r.strip() for r in raw_reason.split("|")]
        return " | ".join(reasons[:2])

    def populate_table(self, table, data_list, action_color):
        table.setSortingEnabled(False)
        table.setColumnCount(12)
        for row, res in enumerate(data_list):
            table.insertRow(row)
            
            direction = res.get("direction", "WAIT")
            symbol = str(res.get("symbol", res.get("Symbol", "")))
            score = float(res.get("score", 0))
            trade_type = res.get("trade_type", "⚡ SCALP" if score >= 65 else "📈 INTRADAY")
            
            entry_val = float(res.get("entry", 0.0))
            sl_val = float(res.get("sl", 0.0))
            tgt_val = float(res.get("target1", 0.0))
            
            e_str = f"{entry_val:.2f}" if entry_val > 0 else "--"
            sl_str = f"{sl_val:.2f}" if sl_val > 0 else "--"
            t_str = f"{tgt_val:.2f}" if tgt_val > 0 else "--"
            rr_str = "1:2.0+" if entry_val > 0 else "--"
            
            if score >= 90: grade = "★★★★★ A+"
            elif score >= 80: grade = "★★★★☆ A"
            elif score >= 70: grade = "★★★☆☆ B"
            else: grade = "★☆☆☆☆ Reject"
            
            items = [
                f"#{row+1}",
                trade_type,
                symbol,
                res.get("sector", "FNO"),
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
                # Right Align numeric cols
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
        
        table.setSortingEnabled(True)

    def export_csv(self):
        import csv
        from datetime import datetime
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        
        default_name = f"intraday_scan_{datetime.now().strftime('%d-%b-%Y')}.csv"
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
