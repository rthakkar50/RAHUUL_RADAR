from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDialog
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush
from ui.styles import CARD_BG, TEXT_PRIMARY

class ViewAllWindow(QDialog):
    symbol_clicked = Signal(str)
    
    def __init__(self, data_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Top 50 Results")
        self.resize(600, 500)
        self.setStyleSheet(f"background-color: {CARD_BG}; color: {TEXT_PRIMARY};")
        
        layout = QVBoxLayout(self)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Symbol", "Score", "Signal", "RS Score", "RS Rank", "RR"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.cellClicked.connect(self.on_cell_clicked)
        
        self.table.setRowCount(len(data_list))
        for row, item in enumerate(data_list):
            symbol = str(item.get("symbol", item.get("Symbol", "--")))
            score = str(item.get("score", item.get("Score", "--")))
            self.table.setItem(row, 0, QTableWidgetItem(symbol))
            self.table.setItem(row, 1, QTableWidgetItem(score))
            
            signal_val = str(item.get("signal", item.get("Signal", "--")))
            signal_item = QTableWidgetItem(signal_val)
            if signal_val == "BUY":
                signal_item.setForeground(QBrush(QColor("#4CAF50")))
            elif signal_val == "SELL":
                signal_item.setForeground(QBrush(QColor("#F44336")))
            elif signal_val == "WATCH":
                signal_item.setForeground(QBrush(QColor("#FF9800")))
                
            self.table.setItem(row, 2, signal_item)
            
            # RS Columns
            rs_score = item.get("rs_score", item.get("RS Score", "--"))
            rs_rank = item.get("rs_rank", item.get("RS Rank", "--"))
            self.table.setItem(row, 3, QTableWidgetItem(str(rs_score)))
            self.table.setItem(row, 4, QTableWidgetItem(str(rs_rank)))
            
            rr = item.get("rr", item.get("RR", "--"))
            self.table.setItem(row, 5, QTableWidgetItem(str(rr)))
            
        layout.addWidget(self.table)

    def on_cell_clicked(self, row, col):
        symbol_item = self.table.item(row, 0)
        if symbol_item:
            self.symbol_clicked.emit(symbol_item.text())
            self.accept() # Close the popup window

class TopBuyTable(QFrame):
    symbol_clicked = Signal(str)
    add_to_watchlist = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("Card")
        self.full_data = []      # list of display dicts
        self.detail_map = {}     # symbol -> full detail dict (with entry/sl/targets)
        layout = QVBoxLayout(self)
        
        # Header Row
        header_layout = QHBoxLayout()
        title = QLabel("TOP BUY")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.view_all_btn = QPushButton("View All")
        self.view_all_btn.setStyleSheet("border: none; background: transparent; text-decoration: underline;")
        self.view_all_btn.setCursor(Qt.PointingHandCursor)
        self.view_all_btn.clicked.connect(self.show_view_all)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.view_all_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Symbol", "Score", "Signal", "RS Score", "RS Rank", "RR", "OI Activity"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 6):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
            self.table.horizontalHeader().resizeSection(i, 80)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.cellDoubleClicked.connect(self.on_cell_clicked)
        
        layout.addWidget(self.table)
        
        self.placeholder = QLabel("No Data")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("color: #A0AAB5; padding: 20px;")
        layout.addWidget(self.placeholder)
        
        self.table.hide()

    def update_data(self, data_list, detail_map=None):
        self.full_data = data_list
        self.detail_map = detail_map or {}
        if not data_list:
            self.table.hide()
            self.placeholder.setText("No Data")
            self.placeholder.show()
            return
            
        self.placeholder.hide()
        self.table.show()
        
        display_data = data_list[:5] # show top 5 here
        self.table.setRowCount(len(display_data))
        for row, item in enumerate(display_data):
            symbol = str(item.get("symbol", item.get("Symbol", "--")))
            score = str(item.get("score", item.get("Score", "--")))
            self.table.setItem(row, 0, QTableWidgetItem(symbol))
            self.table.setItem(row, 1, QTableWidgetItem(score))
            
            signal_val = str(item.get("signal", item.get("Signal", "--")))
            signal_item = QTableWidgetItem(signal_val)
            if signal_val == "BUY":
                signal_item.setForeground(QBrush(QColor("#4CAF50")))
            elif signal_val == "SELL":
                signal_item.setForeground(QBrush(QColor("#F44336")))
            elif signal_val == "WATCH":
                signal_item.setForeground(QBrush(QColor("#FF9800")))
                
            self.table.setItem(row, 2, signal_item)
            
            # RS Columns
            rs_score = item.get("rs_score", item.get("RS Score", 50.0))
            rs_rank = item.get("rs_rank", item.get("RS Rank", f"#{row+1}"))
            if str(rs_rank) == "--":
                rs_rank = f"#{row+1}"
            self.table.setItem(row, 3, QTableWidgetItem(str(rs_score)))
            self.table.setItem(row, 4, QTableWidgetItem(str(rs_rank)))
            
            rr = item.get("rr", item.get("RR", "1:2.0"))
            self.table.setItem(row, 5, QTableWidgetItem(str(rr)))

            # OI Activity column (F&O mode)
            sym = symbol
            oi_data = self.detail_map.get(sym, {}).get("oi_activity")
            if oi_data and isinstance(oi_data, dict):
                emoji    = oi_data.get("emoji", "🟢")
                activity = oi_data.get("activity", "Long Accumulation")
                bias     = oi_data.get("bias", "BULLISH")
                oi_item  = QTableWidgetItem(f"{emoji} {activity}")
                if bias == "BULLISH":
                    oi_item.setForeground(QBrush(QColor("#4CAF50")))
                elif bias == "BEARISH":
                    oi_item.setForeground(QBrush(QColor("#F44336")))
                else:
                    oi_item.setForeground(QBrush(QColor("#FF9800")))
                self.table.setItem(row, 6, oi_item)
            else:
                score_num = float(item.get("score", item.get("Score", 80)) or 80)
                oi_text = "🟢 Long Build-up" if score_num >= 90 else "🟢 Long Accumulation"
                oi_item = QTableWidgetItem(oi_text)
                oi_item.setForeground(QBrush(QColor("#4CAF50")))
                self.table.setItem(row, 6, oi_item)

    def show_view_all(self):
        if not self.full_data:
            return
        self.view_window = ViewAllWindow(self.full_data, self)
        self.view_window.symbol_clicked.connect(self.symbol_clicked.emit)
        self.view_window.exec()
        
    def on_cell_clicked(self, row, col):
        symbol_item = self.table.item(row, 0)
        if not symbol_item:
            return
        sym = symbol_item.text()
        # If we have full detail data, show popup
        if sym in self.detail_map:
            from ui.stock_detail_popup import StockDetailPopup
            popup = StockDetailPopup(self.detail_map[sym], self)
            popup.open_chart.connect(self.symbol_clicked.emit)
            popup.add_to_watchlist.connect(self.add_to_watchlist.emit)
            popup.exec()
        else:
            self.symbol_clicked.emit(sym)

class TopSellTable(QFrame):
    symbol_clicked = Signal(str)
    add_to_watchlist = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("Card")
        self.full_data = []
        self.detail_map = {}
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        title = QLabel("TOP SELL")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.view_all_btn = QPushButton("View All")
        self.view_all_btn.setStyleSheet("border: none; background: transparent; text-decoration: underline;")
        self.view_all_btn.setCursor(Qt.PointingHandCursor)
        self.view_all_btn.clicked.connect(self.show_view_all)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.view_all_btn)
        
        layout.addLayout(header_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Symbol", "Score", "Signal", "RS Score", "RS Rank", "RR", "OI Activity"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 6):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
            self.table.horizontalHeader().resizeSection(i, 80)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.cellDoubleClicked.connect(self.on_cell_clicked)
        
        layout.addWidget(self.table)
        
        self.placeholder = QLabel("No Data")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("color: #A0AAB5; padding: 20px;")
        layout.addWidget(self.placeholder)
        
        self.table.hide()

    def update_data(self, data_list, detail_map=None):
        self.full_data = data_list
        self.detail_map = detail_map or {}
        if not data_list:
            self.table.hide()
            self.placeholder.setText("No Data")
            self.placeholder.show()
            return
            
        self.placeholder.hide()
        self.table.show()
        
        display_data = data_list[:5]
        self.table.setRowCount(len(display_data))
        for row, item in enumerate(display_data):
            symbol = str(item.get("symbol", item.get("Symbol", "--")))
            score = str(item.get("score", item.get("Score", "--")))
            self.table.setItem(row, 0, QTableWidgetItem(symbol))
            self.table.setItem(row, 1, QTableWidgetItem(score))
            
            signal_val = str(item.get("signal", item.get("Signal", "--")))
            signal_item = QTableWidgetItem(signal_val)
            if signal_val == "BUY":
                signal_item.setForeground(QBrush(QColor("#4CAF50")))
            elif signal_val == "SELL":
                signal_item.setForeground(QBrush(QColor("#F44336")))
            elif signal_val == "WATCH":
                signal_item.setForeground(QBrush(QColor("#FF9800")))
                
            self.table.setItem(row, 2, signal_item)
            
            rs_score = item.get("rs_score", item.get("RS Score", "--"))
            rs_rank = item.get("rs_rank", item.get("RS Rank", "--"))
            self.table.setItem(row, 3, QTableWidgetItem(str(rs_score)))
            self.table.setItem(row, 4, QTableWidgetItem(str(rs_rank)))
            
            rr = item.get("rr", item.get("RR", "--"))
            self.table.setItem(row, 5, QTableWidgetItem(str(rr)))
            
            sym = symbol
            oi_data = self.detail_map.get(sym, {}).get("oi_activity")
            if oi_data:
                emoji = oi_data.get("emoji", "⛔")
                activity = oi_data.get("activity", "--")
                bias = oi_data.get("bias", "NEUTRAL")
                oi_item = QTableWidgetItem(f"{emoji} {activity}")
                if bias == "BULLISH":
                    oi_item.setForeground(QBrush(QColor("#4CAF50")))
                elif bias == "BEARISH":
                    oi_item.setForeground(QBrush(QColor("#F44336")))
                else:
                    oi_item.setForeground(QBrush(QColor("#888888")))
                self.table.setItem(row, 6, oi_item)
            else:
                self.table.setItem(row, 6, QTableWidgetItem(str(item.get("oi_activity", item.get("OI Activity", "--")))))

    def show_view_all(self):
        if not self.full_data:
            return
        self.view_window = ViewAllWindow(self.full_data, self)
        self.view_window.symbol_clicked.connect(self.symbol_clicked.emit)
        self.view_window.exec()
        
    def on_cell_clicked(self, row, col):
        symbol_item = self.table.item(row, 0)
        if not symbol_item:
            return
        sym = symbol_item.text()
        if sym in self.detail_map:
            from ui.stock_detail_popup import StockDetailPopup
            popup = StockDetailPopup(self.detail_map[sym], self)
            popup.open_chart.connect(self.symbol_clicked.emit)
            popup.add_to_watchlist.connect(self.add_to_watchlist.emit)
            popup.exec()
        else:
            self.symbol_clicked.emit(sym)

class TopWatchTable(QFrame):
    symbol_clicked = Signal(str)
    add_to_watchlist = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("Card")
        self.full_data = []
        self.detail_map = {}
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        title = QLabel("TOP WATCH")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.view_all_btn = QPushButton("View All")
        self.view_all_btn.setStyleSheet("border: none; background: transparent; text-decoration: underline;")
        self.view_all_btn.setCursor(Qt.PointingHandCursor)
        self.view_all_btn.clicked.connect(self.show_view_all)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.view_all_btn)
        
        layout.addLayout(header_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Symbol", "Score", "Signal", "RS Score", "RS Rank", "RR", "OI Activity"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 6):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
            self.table.horizontalHeader().resizeSection(i, 80)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.cellDoubleClicked.connect(self.on_cell_clicked)
        
        layout.addWidget(self.table)
        
        self.placeholder = QLabel("No Data")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("color: #A0AAB5; padding: 20px;")
        layout.addWidget(self.placeholder)
        
        self.table.hide()

    def update_data(self, data_list, detail_map=None):
        self.full_data = data_list
        self.detail_map = detail_map or {}
        if not data_list:
            self.table.hide()
            self.placeholder.setText("No Data")
            self.placeholder.show()
            return
            
        self.placeholder.hide()
        self.table.show()
        
        display_data = data_list[:5]
        self.table.setRowCount(len(display_data))
        for row, item in enumerate(display_data):
            symbol = str(item.get("symbol", item.get("Symbol", "--")))
            score = str(item.get("score", item.get("Score", "--")))
            self.table.setItem(row, 0, QTableWidgetItem(symbol))
            self.table.setItem(row, 1, QTableWidgetItem(score))
            
            signal_val = str(item.get("signal", item.get("Signal", "--")))
            signal_item = QTableWidgetItem(signal_val)
            if signal_val == "BUY":
                signal_item.setForeground(QBrush(QColor("#4CAF50")))
            elif signal_val == "SELL":
                signal_item.setForeground(QBrush(QColor("#F44336")))
            elif signal_val == "WATCH":
                signal_item.setForeground(QBrush(QColor("#FF9800")))
                
            self.table.setItem(row, 2, signal_item)
            
            rs_score = item.get("rs_score", item.get("RS Score", "--"))
            rs_rank = item.get("rs_rank", item.get("RS Rank", "--"))
            self.table.setItem(row, 3, QTableWidgetItem(str(rs_score)))
            self.table.setItem(row, 4, QTableWidgetItem(str(rs_rank)))
            
            rr = item.get("rr", item.get("RR", "--"))
            self.table.setItem(row, 5, QTableWidgetItem(str(rr)))
            
            sym = symbol
            oi_data = self.detail_map.get(sym, {}).get("oi_activity")
            if oi_data:
                emoji = oi_data.get("emoji", "⛔")
                activity = oi_data.get("activity", "--")
                bias = oi_data.get("bias", "NEUTRAL")
                oi_item = QTableWidgetItem(f"{emoji} {activity}")
                if bias == "BULLISH":
                    oi_item.setForeground(QBrush(QColor("#4CAF50")))
                elif bias == "BEARISH":
                    oi_item.setForeground(QBrush(QColor("#F44336")))
                else:
                    oi_item.setForeground(QBrush(QColor("#888888")))
                self.table.setItem(row, 6, oi_item)
            else:
                self.table.setItem(row, 6, QTableWidgetItem(str(item.get("oi_activity", item.get("OI Activity", "--")))))

    def show_view_all(self):
        if not self.full_data:
            return
        self.view_window = ViewAllWindow(self.full_data, self)
        self.view_window.symbol_clicked.connect(self.symbol_clicked.emit)
        self.view_window.exec()
        
    def on_cell_clicked(self, row, col):
        symbol_item = self.table.item(row, 0)
        if not symbol_item:
            return
        sym = symbol_item.text()
        if sym in self.detail_map:
            from ui.stock_detail_popup import StockDetailPopup
            popup = StockDetailPopup(self.detail_map[sym], self)
            popup.open_chart.connect(self.symbol_clicked.emit)
            popup.add_to_watchlist.connect(self.add_to_watchlist.emit)
            popup.exec()
        else:
            self.symbol_clicked.emit(sym)

