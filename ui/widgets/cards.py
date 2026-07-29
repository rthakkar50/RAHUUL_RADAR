from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PySide6.QtCore import Qt, Signal
from ui.styles import COLOR_BUY, COLOR_SELL, COLOR_WATCH

class BestTradeCard(QFrame):
    clicked = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setObjectName("PremiumCard")
        self.setCursor(Qt.PointingHandCursor)
        layout = QVBoxLayout(self)
        
        title = QLabel("Today's Best Trade")
        title.setObjectName("PremiumTitle")
        layout.addWidget(title)
        
        grid = QGridLayout()
        self.val_symbol = QLabel("--")
        self.val_symbol.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        self.val_signal = QLabel("--")
        self.val_grade = QLabel("--")
        self.val_entry = QLabel("--")
        self.val_sl = QLabel("--")
        self.val_target1 = QLabel("--")
        self.val_target2 = QLabel("--")
        self.val_rr = QLabel("--")
        self.val_confidence = QLabel("--")
        
        grid.addWidget(QLabel("Symbol:"), 0, 0)
        grid.addWidget(self.val_symbol, 0, 1)
        grid.addWidget(QLabel("Signal:"), 1, 0)
        grid.addWidget(self.val_signal, 1, 1)
        grid.addWidget(QLabel("Grade:"), 2, 0)
        grid.addWidget(self.val_grade, 2, 1)
        grid.addWidget(QLabel("Confidence:"), 3, 0)
        grid.addWidget(self.val_confidence, 3, 1)
        grid.addWidget(QLabel("Entry:"), 4, 0)
        grid.addWidget(self.val_entry, 4, 1)
        grid.addWidget(QLabel("SL:"), 5, 0)
        grid.addWidget(self.val_sl, 5, 1)
        grid.addWidget(QLabel("Target 1:"), 6, 0)
        grid.addWidget(self.val_target1, 6, 1)
        grid.addWidget(QLabel("Target 2:"), 7, 0)
        grid.addWidget(self.val_target2, 7, 1)
        grid.addWidget(QLabel("Risk Reward:"), 8, 0)
        grid.addWidget(self.val_rr, 8, 1)
        
        layout.addLayout(grid)
        layout.addStretch()
        
    def mousePressEvent(self, event):
        symbol = self.val_symbol.text()
        if symbol != "--":
            self.clicked.emit(symbol)
        super().mousePressEvent(event)
        
    def update_data(self, data):
        if not data:
            return
        sym = str(data.get("symbol") or data.get("Symbol") or "--").replace(".NS", "")
        sig = str(data.get("signal") or data.get("Signal") or "--").upper()
        grade = str(data.get("grade") or data.get("Grade") or ("A+" if "BUY" in sig else "--"))
        conf = data.get("confidence") or data.get("Confidence") or "--"
        if conf != "--":
            try:
                conf = f"{float(conf):.1f}%"
            except Exception:
                conf = f"{conf}%"

        price = data.get("entry") or data.get("Entry") or data.get("price") or data.get("Price") or "--"
        sl = data.get("sl") or data.get("Stop Loss") or "--"
        t1 = data.get("target1") or data.get("Target 1") or "--"
        t2 = data.get("target2") or data.get("Target 2") or "--"
        rr = data.get("rr") or data.get("Risk Reward") or data.get("RR") or "--"

        self.val_symbol.setText(sym)
        self.val_signal.setText(sig)
        if "BUY" in sig:
            self.val_signal.setStyleSheet(f"color: {COLOR_BUY}; font-weight: bold;")
        elif "SELL" in sig:
            self.val_signal.setStyleSheet(f"color: {COLOR_SELL}; font-weight: bold;")
        else:
            self.val_signal.setStyleSheet("")

        self.val_grade.setText(grade)
        self.val_confidence.setText(str(conf))
        self.val_entry.setText(f"₹{float(price):,.2f}" if isinstance(price, (int, float)) or (isinstance(price, str) and price.replace(".","").isdigit()) else str(price))
        self.val_sl.setText(f"₹{float(sl):,.2f}" if isinstance(sl, (int, float)) or (isinstance(sl, str) and sl.replace(".","").isdigit()) else str(sl))
        self.val_target1.setText(f"₹{float(t1):,.2f}" if isinstance(t1, (int, float)) or (isinstance(t1, str) and t1.replace(".","").isdigit()) else str(t1))
        self.val_target2.setText(f"₹{float(t2):,.2f}" if isinstance(t2, (int, float)) or (isinstance(t2, str) and t2.replace(".","").isdigit()) else str(t2))
        self.val_rr.setText(str(rr))

class ScanStatsCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        
        title = QLabel("Scan Statistics")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        grid = QGridLayout()
        
        self.val_total = QLabel("No Data")
        grid.addWidget(QLabel("Total Stocks :"), 0, 0)
        grid.addWidget(self.val_total, 0, 1)
        
        buy_lbl = QLabel("BUY        :")
        self.val_buy = QLabel("No Data")
        self.val_buy.setStyleSheet(f"color: {COLOR_BUY}; font-weight: bold;")
        grid.addWidget(buy_lbl, 1, 0)
        grid.addWidget(self.val_buy, 1, 1)
        
        strong_lbl = QLabel("Strong BUY :")
        self.val_strong = QLabel("No Data")
        self.val_strong.setStyleSheet(f"color: {COLOR_BUY}; font-weight: bold;")
        grid.addWidget(strong_lbl, 2, 0)
        grid.addWidget(self.val_strong, 2, 1)
        
        watch_lbl = QLabel("WATCH      :")
        self.val_watch = QLabel("No Data")
        self.val_watch.setStyleSheet(f"color: {COLOR_WATCH}; font-weight: bold;")
        grid.addWidget(watch_lbl, 3, 0)
        grid.addWidget(self.val_watch, 3, 1)
        
        sell_lbl = QLabel("SELL       :")
        self.val_sell = QLabel("No Data")
        self.val_sell.setStyleSheet(f"color: {COLOR_SELL}; font-weight: bold;")
        grid.addWidget(sell_lbl, 4, 0)
        grid.addWidget(self.val_sell, 4, 1)
        
        self.val_score = QLabel("No Data")
        grid.addWidget(QLabel("Avg Score  :"), 5, 0)
        grid.addWidget(self.val_score, 5, 1)
        
        layout.addLayout(grid)
        layout.addStretch()

    def update_data(self, data):
        if not data:
            self.val_total.setText("No Data")
            self.val_buy.setText("No Data")
            self.val_strong.setText("No Data")
            self.val_watch.setText("No Data")
            self.val_sell.setText("No Data")
            self.val_score.setText("No Data")
            return
        self.val_total.setText(str(data.get("total", "No Data")))
        self.val_buy.setText(str(data.get("buy", "No Data")))
        self.val_strong.setText(str(data.get("strong_buy", "No Data")))
        self.val_watch.setText(str(data.get("watch", "No Data")))
        self.val_sell.setText(str(data.get("sell", "No Data")))
        self.val_score.setText(str(data.get("avg_score", "No Data")))
