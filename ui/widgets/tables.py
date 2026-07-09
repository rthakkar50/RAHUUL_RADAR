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
            self.table.setItem(row, 0, QTableWidgetItem(item["symbol"]))
            self.table.setItem(row, 1, QTableWidgetItem(item["score"]))
            
            signal_item = QTableWidgetItem(item["signal"])
            if item["signal"] == "BUY":
                signal_item.setForeground(QBrush(QColor("#4CAF50")))
            elif item["signal"] == "SELL":
                signal_item.setForeground(QBrush(QColor("#F44336")))
            elif item["signal"] == "WATCH":
                signal_item.setForeground(QBrush(QColor("#FF9800")))
                
            self.table.setItem(row, 2, signal_item)
            
            # RS Columns
            rs_score = item.get("rs_score", "--")
            rs_rank = item.get("rs_rank", "--")
            self.table.setItem(row, 3, QTableWidgetItem(str(rs_score)))
            self.table.setItem(row, 4, QTableWidgetItem(str(rs_rank)))
            
            self.table.setItem(row, 5, QTableWidgetItem(item["rr"]))
            
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
        
        self.placeholder = QLabel("No Scan Performed Yet")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("color: #A0AAB5; padding: 20px;")
        layout.addWidget(self.placeholder)
        
        self.table.hide()

    def update_data(self, data_list, detail_map=None):
        self.full_data = data_list
        self.detail_map = detail_map or {}
        if not data_list:
            self.table.hide()
            self.placeholder.setText("No 'BUY' setups found in current scan.")
            self.placeholder.show()
            return
            
        self.placeholder.hide()
        self.table.show()
        
        display_data = data_list[:5] # show top 5 here
        self.table.setRowCount(len(display_data))
        for row, item in enumerate(display_data):
            self.table.setItem(row, 0, QTableWidgetItem(item["symbol"]))
            self.table.setItem(row, 1, QTableWidgetItem(item["score"]))
            
            signal_item = QTableWidgetItem(item["signal"])
            if item["signal"] == "BUY":
                signal_item.setForeground(QBrush(QColor("#4CAF50")))
            elif item["signal"] == "SELL":
                signal_item.setForeground(QBrush(QColor("#F44336")))
            elif item["signal"] == "WATCH":
                signal_item.setForeground(QBrush(QColor("#FF9800")))
                
            self.table.setItem(row, 2, signal_item)
            
            # RS Columns
            rs_score = item.get("rs_score", "--")
            rs_rank = item.get("rs_rank", "--")
            self.table.setItem(row, 3, QTableWidgetItem(str(rs_score)))
            self.table.setItem(row, 4, QTableWidgetItem(str(rs_rank)))
            
            self.table.setItem(row, 5, QTableWidgetItem(item["rr"]))

            # OI Activity column (F&O mode only)
            sym = item["symbol"]
            oi_data = self.detail_map.get(sym, {}).get("oi_activity")
            if oi_data:
                emoji    = oi_data.get("emoji", "⛔")
                activity = oi_data.get("activity", "--")
                bias     = oi_data.get("bias", "NEUTRAL")
                oi_item  = QTableWidgetItem(f"{emoji} {activity}")
                if bias == "BULLISH":
                    oi_item.setForeground(QBrush(QColor("#4CAF50")))
                elif bias == "BEARISH":
                    oi_item.setForeground(QBrush(QColor("#F44336")))
                else:
                    oi_item.setForeground(QBrush(QColor("#888888")))
                self.table.setItem(row, 6, oi_item)
            else:
                self.table.setItem(row, 6, QTableWidgetItem("--"))

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
