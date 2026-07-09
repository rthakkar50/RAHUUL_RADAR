from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QStackedWidget, QScrollArea, QFrame, QSizePolicy
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QCursor
from data.stocks import TOP_50_STOCKS
from ui.styles import CARD_BG, BG_COLOR, BTN_BLUE

SECTORS = {
    "BANK": "^NSEBANK",
    "IT": "^CNXIT",
    "AUTO": "^CNXAUTO",
    "PHARMA": "^CNXPHARMA",
    "METAL": "^CNXMETAL",
    "FMCG": "^CNXFMCG",
    "ENERGY": "^CNXENERGY",
    "REALTY": "^CNXREALTY",
    "PSU": "^CNXPSUBANK",
    "FINANCE": "^CNXFIN"
}

class HeatmapWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, symbols):
        super().__init__()
        self.symbols = symbols

    def run(self):
        try:
            from core.market_data_service import MarketDataService
            svc = MarketDataService()
            
            # Add .NS to stocks, but sectors are already formatted
            formatted_symbols = []
            for sym in self.symbols:
                if sym.startswith("^"):
                    formatted_symbols.append(sym)
                else:
                    formatted_symbols.append(f"{sym}.NS" if not sym.endswith(".NS") else sym)
                    
            results = {}
            
            if len(formatted_symbols) == 1:
                sym = formatted_symbols[0]
                df = svc.get_historical_data(sym, period="5d", interval="1d")
                if df is not None and not df.empty and 'Close' in df:
                    closes = df['Close'].dropna().values
                    if len(closes) >= 2:
                        last = closes[-1]
                        prev = closes[-2]
                        pct = ((last - prev) / prev) * 100
                        results[self.symbols[0]] = {"price": last, "change": pct}
            else:
                for orig_sym, fetch_sym in zip(self.symbols, formatted_symbols):
                    df = svc.get_historical_data(fetch_sym, period="5d", interval="1d")
                    if df is not None and not df.empty and 'Close' in df:
                        closes = df['Close'].dropna().values
                        if len(closes) >= 2:
                            last = closes[-1]
                            prev = closes[-2]
                            pct = ((last - prev) / prev) * 100
                            results[orig_sym] = {"price": last, "change": pct}
            
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))

class HeatmapBlock(QFrame):
    clicked = Signal(str)

    def __init__(self, name, display_name=None):
        super().__init__()
        self.name = name
        self.display_name = display_name or name
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setMinimumSize(180, 80)
        self.setMaximumHeight(90)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Top row: Name
        self.lbl_name = QLabel(self.display_name)
        self.lbl_name.setFont(QFont("Arial", 11, QFont.Bold))
        self.lbl_name.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Bottom row: Price and % Change
        bottom_layout = QHBoxLayout()
        self.lbl_price = QLabel("")
        self.lbl_price.setFont(QFont("Arial", 11, QFont.Bold))
        self.lbl_price.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        
        self.lbl_val = QLabel("Loading...")
        self.lbl_val.setFont(QFont("Arial", 11, QFont.Bold))
        self.lbl_val.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        
        bottom_layout.addWidget(self.lbl_price)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.lbl_val)
        
        self.layout.addWidget(self.lbl_name)
        self.layout.addLayout(bottom_layout)
        
        self.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 4px; color: white;")
        
    def mousePressEvent(self, event):
        self.clicked.emit(self.name)
        
    def update_data(self, price, change):
        if price is not None and price > 0:
            self.lbl_price.setText(f"{price:,.2f}")
        else:
            self.lbl_price.setText("--")
            
        if change is not None:
            self.lbl_val.setText(f"{change:+.2f}%")
            if change > 1.5:
                color = "#1E8E3E" # Dark Green
            elif change > 0:
                color = "#5BB974" # Light Green
            elif change < -1.5:
                color = "#D93025" # Dark Red
            elif change < 0:
                color = "#E67C73" # Light Red
            else:
                color = "#757575" # Gray
        else:
            self.lbl_val.setText("--%")
            color = "#757575" # Gray
            
        self.setStyleSheet(f"background-color: {color}; border-radius: 4px; color: white;")

class HeatmapScreen(QWidget):
    navigate_to_chart = Signal(str)

    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QHBoxLayout()
        self.lbl_title = QLabel("Market Heatmap")
        self.lbl_title.setFont(QFont("Arial", 24, QFont.Bold))
        self.btn_back = QPushButton("← Back to Sectors")
        self.btn_back.setStyleSheet(f"background-color: {BTN_BLUE}; color: white; padding: 8px 15px; border-radius: 4px; border: none; font-weight: bold;")
        self.btn_back.clicked.connect(self.show_sectors)
        self.btn_back.hide()
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setStyleSheet(f"background-color: #3D4047; color: white; padding: 8px 15px; border-radius: 4px; border: none; font-weight: bold;")
        self.btn_refresh.clicked.connect(self.refresh_current)
        
        header.addWidget(self.lbl_title)
        header.addWidget(self.btn_back)
        header.addStretch()
        header.addWidget(self.btn_refresh)
        main_layout.addLayout(header)
        
        # Stacked Widget
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # 1. Sector View
        self.sector_view = QWidget()
        self.sector_layout = QGridLayout(self.sector_view)
        self.sector_layout.setSpacing(10)
        self.stack.addWidget(self.sector_view)
        
        # 2. Stock View
        self.stock_scroll = QScrollArea()
        self.stock_scroll.setWidgetResizable(True)
        self.stock_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.stock_view = QWidget()
        self.stock_layout = QGridLayout(self.stock_view)
        self.stock_layout.setSpacing(10)
        self.stock_scroll.setWidget(self.stock_view)
        
        self.stack.addWidget(self.stock_scroll)
        
        self.blocks = {}
        self.worker = None
        self.current_mode = "SECTOR" # SECTOR or specific sector name
        
        self.init_sectors()
        
    def init_sectors(self):
        # Clear layout
        while self.sector_layout.count():
            item = self.sector_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self.blocks.clear()
        
        row, col = 0, 0
        for name, _ in SECTORS.items():
            block = HeatmapBlock(name, name)
            block.clicked.connect(self.on_sector_clicked)
            self.sector_layout.addWidget(block, row, col)
            self.blocks[name] = block
            
            col += 1
            if col > 4:  # Wrap at 5 columns (2 rows of 5 for 10 sectors)
                col = 0
                row += 1
                
        self.load_sector_data()
        
    def load_sector_data(self):
        symbols = list(SECTORS.values())
        # Map back symbols to names in the worker result
        self.worker = HeatmapWorker(symbols)
        self.worker.finished.connect(self.on_sector_data_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
    def on_sector_data_loaded(self, results):
        for name, symbol in SECTORS.items():
            if symbol in results:
                data = results[symbol]
                if name in self.blocks:
                    self.blocks[name].update_data(data['price'], data['change'])
            else:
                if name in self.blocks:
                    self.blocks[name].update_data(0.0, None)
                    
    def on_sector_clicked(self, sector_name):
        self.current_mode = sector_name
        self.lbl_title.setText(f"{sector_name} Heatmap")
        self.btn_back.show()
        self.stack.setCurrentIndex(1)
        
        # Clear layout
        while self.stock_layout.count():
            item = self.stock_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self.blocks.clear()
        
        stocks_in_sector = [s.symbol for s in TOP_50_STOCKS if s.sector == sector_name]
        
        row, col = 0, 0
        for sym in stocks_in_sector:
            block = HeatmapBlock(sym, sym)
            block.clicked.connect(self.on_stock_clicked)
            self.stock_layout.addWidget(block, row, col)
            self.blocks[sym] = block
            
            col += 1
            if col > 5: # Match the 6-column grid from the image
                col = 0
                row += 1
                
        if stocks_in_sector:
            self.worker = HeatmapWorker(stocks_in_sector)
            self.worker.finished.connect(self.on_stock_data_loaded)
            self.worker.error.connect(self.on_error)
            self.worker.start()
            
    def on_stock_clicked(self, stock_symbol):
        self.navigate_to_chart.emit(stock_symbol)
            
    def on_stock_data_loaded(self, results):
        for sym in self.blocks.keys():
            if sym in results:
                data = results[sym]
                self.blocks[sym].update_data(data['price'], data['change'])
            else:
                self.blocks[sym].update_data(0.0, None)
                
    def on_error(self, err_msg):
        # Set all active blocks to placeholder on error
        for block in self.blocks.values():
            block.update_data(0.0, None)
                
    def show_sectors(self):
        self.current_mode = "SECTOR"
        self.lbl_title.setText("Market Heatmap")
        self.btn_back.hide()
        self.stack.setCurrentIndex(0)
        self.init_sectors()
        
    def refresh_current(self):
        if self.current_mode == "SECTOR":
            self.init_sectors()
        else:
            self.on_sector_clicked(self.current_mode)
