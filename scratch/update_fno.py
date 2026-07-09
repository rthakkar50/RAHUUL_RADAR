import os

fno_path = "/Users/pr/RAHUUL_RADAR/ui/fno_scanner.py"
with open(fno_path, "r") as f:
    content = f.read()

# 1. Replace FnoScannerWorker with RankingScanThread
new_thread = """class RankingScanThread(QThread):
    progress = Signal(int)
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
            symbols = [item["symbol"] for item in FNO_UNIVERSE]
            total = len(symbols)
            
            all_results = []
            stats = {"Total": total, "Processed": 0, "Rejected": 0}
            
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
                    
                self.progress.emit(int(((idx + 1) / total) * 100))
                
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
"""

# Replace between class FnoScannerWorker and class FnoScannerScreen
start_idx = content.find("class FnoScannerWorker")
end_idx = content.find("class FnoScannerScreen")
content = content[:start_idx] + new_thread + "\n\n" + content[end_idx:]

# 2. Modify FnoScannerScreen to use the new layout
# Replace the data table part (from self.table = QTableWidget() up to layout.addWidget(self.table))
table_start = content.find("self.table = QTableWidget()")
table_end = content.find("layout.addWidget(self.table)") + len("layout.addWidget(self.table)")

new_tables = """        from PySide6.QtWidgets import QSplitter
        splitter = QSplitter(Qt.Vertical)
        
        # Top Buys
        buy_frame = QFrame()
        buy_layout = QVBoxLayout(buy_frame)
        buy_layout.setContentsMargins(0, 0, 0, 0)
        lbl_buy = QLabel("🟢 TOP 10 BUY OPPORTUNITIES")
        lbl_buy.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 16px;")
        buy_layout.addWidget(lbl_buy)
        self.buy_table = self.create_table()
        buy_layout.addWidget(self.buy_table)
        splitter.addWidget(buy_frame)
        
        # Top Sells
        sell_frame = QFrame()
        sell_layout = QVBoxLayout(sell_frame)
        sell_layout.setContentsMargins(0, 0, 0, 0)
        lbl_sell = QLabel("🔴 TOP 10 SELL OPPORTUNITIES")
        lbl_sell.setStyleSheet("color: #F44336; font-weight: bold; font-size: 16px;")
        sell_layout.addWidget(lbl_sell)
        self.sell_table = self.create_table()
        sell_layout.addWidget(self.sell_table)
        splitter.addWidget(sell_frame)
        
        # Top Watch
        watch_frame = QFrame()
        watch_layout = QVBoxLayout(watch_frame)
        watch_layout.setContentsMargins(0, 0, 0, 0)
        lbl_watch = QLabel("⚪ TOP 10 WATCH OPPORTUNITIES")
        lbl_watch.setStyleSheet("color: #FFC107; font-weight: bold; font-size: 16px;")
        watch_layout.addWidget(lbl_watch)
        self.watch_table = self.create_table()
        watch_layout.addWidget(self.watch_table)
        splitter.addWidget(watch_frame)
        
        layout.addWidget(splitter)
"""
content = content[:table_start] + new_tables + content[table_end:]

# Inject create_table method inside FnoScannerScreen right before on_cell_clicked
create_table_method = """
    def create_table(self):
        from PySide6.QtWidgets import QAbstractItemView
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Rank", "Symbol", "Grade", "Final Score", "Confidence", "Risk Reward", "Top 3 Reasons"
        ])
        header_view = table.horizontalHeader()
        header_view.setSectionResizeMode(6, QHeaderView.Stretch)
        table.setStyleSheet("QTableWidget { background-color: #22242D; border: 1px solid #3D4047; border-radius: 8px; color: white; } QHeaderView::section { background-color: #1A1C23; padding: 8px; font-weight: bold; color: gray; }")
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        return table
"""
cell_clicked_idx = content.find("def on_cell_clicked")
content = content[:cell_clicked_idx] + create_table_method + content[cell_clicked_idx:]

# Remove old apply_filters since we're using split tables now, and replace scan_finished
old_apply_filters_start = content.find("def apply_filters")
# We'll just replace scan_finished entirely
scan_finished_start = content.find("def scan_finished(self, results):")
add_to_watchlist_start = content.find("def _add_to_watchlist")

new_scan_finished = """    def scan_finished(self, top_buys, top_sells, top_watch, stats):
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("⚡ Scan F&O Options")
        self.market_status.setText(get_market_status())

        dt_now = datetime.now()
        self.last_scan.setText(f"{dt_now.strftime('%d-%b-%Y')}\\n{dt_now.strftime('%H:%M:%S')}")

        self.progress_bar.hide()
        
        # We can update the best trade card with the top buy if any
        if top_buys:
            best = top_buys[0]
            # Mapped to match UI expectations
            best_ui = {
                "signal": "BUY",
                "symbol": best["symbol"],
                "score": best["score"]
            }
            self.best_trade_card.update_data(best_ui)
        
        self.buy_table.setRowCount(0)
        self.sell_table.setRowCount(0)
        self.watch_table.setRowCount(0)
        
        self.populate_table(self.buy_table, top_buys, "#4CAF50")
        self.populate_table(self.sell_table, top_sells, "#F44336")
        self.populate_table(self.watch_table, top_watch, "#FFC107")

    def populate_table(self, table, data_list, action_color):
        for row, res in enumerate(data_list):
            table.insertRow(row)
            items = [
                f"#{row+1}",
                str(res.get("symbol", "")),
                str(res.get("grade", "")),
                str(res.get("score", "")),
                f"{res.get('confidence', '')}%",
                "1:2.0+",
                str(res.get("reason", ""))
            ]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                if col == 0:
                    font = item.font(); font.setBold(True); item.setFont(font)
                    item.setForeground(QColor(action_color))
                elif col == 2:
                    item.setForeground(QColor("#FFC107"))
                    font = item.font(); font.setBold(True); item.setFont(font)
                elif col == 3:
                    font = item.font(); font.setBold(True); item.setFont(font)
                    if res.get("score", 0) >= 80:
                        item.setForeground(QColor("#4CAF50"))
                table.setItem(row, col, item)

"""
content = content[:scan_finished_start] + new_scan_finished + content[add_to_watchlist_start:]


# Update start_scan to use RankingScanThread
start_scan_start = content.find("self.scanner = FnoScannerWorker()")
start_scan_end = content.find("self.scanner.start()") + len("self.scanner.start()")

new_start_scan = """self.scanner = RankingScanThread()
        self.scanner.progress.connect(self.update_progress)
        self.scanner.finished_scan.connect(self.scan_finished)
        self.scanner.start()"""
        
content = content[:start_scan_start] + new_start_scan + content[start_scan_end:]

with open(fno_path, "w") as f:
    f.write(content)
