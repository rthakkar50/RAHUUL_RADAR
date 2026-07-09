from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtCore import Qt

class ScannerResultsTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #131722;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #2A2E39;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #131722;
                height: 8px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #2A2E39;
                min-width: 30px;
                border-radius: 4px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        self.verticalHeader().setDefaultSectionSize(42)
        self.horizontalHeader().setStretchLastSection(True)
        
        self.headers = [
            "★", "Rank", "Symbol", "Sector", 
            "Signal", "Grade", "Score", "Confidence", 
            "Entry", "SL", "Target", "RR", 
            "Volume", "Last Price", "Change %", "Reasons"
        ]
        self.setColumnCount(len(self.headers))
        self.setHorizontalHeaderLabels(self.headers)
        
        self.setAlternatingRowColors(True)
        
        font = self.font()
        font.setPointSize(14)
        self.setFont(font)
        
        header_font = self.horizontalHeader().font()
        header_font.setPointSize(13)
        header_font.setBold(True)
        self.horizontalHeader().setFont(header_font)
        
        self._align_headers()

    def _align_headers(self):
        header = self.horizontalHeader()
        header.setMinimumSectionSize(30)
        
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.resizeSection(0, 35) # ★
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.resizeSection(1, 55) # Rank
        for i in range(2, 15):
            header.setSectionResizeMode(i, QHeaderView.Interactive)
            header.resizeSection(i, 80)
        
        header.resizeSection(2, 120) # Symbol
        header.resizeSection(3, 90) # Sector
        header.setSectionResizeMode(15, QHeaderView.Stretch) # Reasons
        
        # Advanced Columns (Hidden by default unless explicitly toggled)
        # Entry (8), SL (9), Target (10), RR (11) are now VISIBLE by default
        for i in range(12, 15):
            self.setColumnHidden(i, True)

    def toggle_advanced_columns(self, visible):
        for i in range(12, 15):
            self.setColumnHidden(i, not visible)

    def populate(self, results):
        self.setSortingEnabled(False)
        self.clearContents()
        self.setRowCount(len(results))
        
        for row, r in enumerate(results):
            # Dynamic Signal Alias Mapping
            sig = str(r.get("Signal", "WAIT")).upper()
            if "BULLISH" in sig: sig = "BUY"
            elif "BEARISH" in sig: sig = "SELL"
            
            def create_item(text="", data=None, align=Qt.AlignCenter):
                item = QTableWidgetItem(str(text))
                if data is not None:
                    item.setData(Qt.EditRole, data)
                item.setTextAlignment(align)
                return item

            # 0 ★
            star = create_item("☆")
            star.setData(Qt.UserRole, r) # Store full dict for filtering/selection
            self.setItem(row, 0, star)
            
            # 1 Rank
            rank = r.get("Rank", row + 1)
            self.setItem(row, 1, create_item(rank, data=rank))
            
            # 2 Symbol
            sym_item = create_item(r.get("Symbol", r.get("symbol", "")))
            sym_font = sym_item.font()
            sym_font.setBold(True)
            sym_item.setFont(sym_font)
            self.setItem(row, 2, sym_item)
            
            # 3 Sector
            self.setItem(row, 3, create_item(r.get("Sector", "")))
            
            # 4 Signal
            sig_item = create_item(sig)
            sig_font = sig_item.font()
            sig_font.setBold(True)
            sig_item.setFont(sig_font)
            if sig == "BUY": sig_item.setForeground(QBrush(QColor("#00B69B")))
            elif sig == "SELL": sig_item.setForeground(QBrush(QColor("#F9322C")))
            elif sig == "WATCH": sig_item.setForeground(QBrush(QColor("#F1C40F")))
            self.setItem(row, 4, sig_item)
            
            # 5 Grade
            grade_val = str(r.get("Trade Grade", r.get("trade_grade", "")))
            grade_item = create_item(grade_val if grade_val else "--")
            if "★★★★★" in grade_val: grade_item.setForeground(QBrush(QColor("#00B69B")))
            elif "★★★★" in grade_val: grade_item.setForeground(QBrush(QColor("#2962FF")))
            elif "★★★" in grade_val: grade_item.setForeground(QBrush(QColor("#00BCD4")))
            elif "★★" in grade_val: grade_item.setForeground(QBrush(QColor("#F1C40F")))
            else: grade_item.setForeground(QBrush(QColor("#9E9E9E")))
            self.setItem(row, 5, grade_item)
            
            # 6 Score
            try: score_val = float(r.get("Score", 0))
            except: score_val = 0.0
            score_display = f"{score_val:.1f}" if score_val > 0 else "--"
            item_score = create_item(score_display, data=score_val)
            if score_val >= 90: item_score.setForeground(QBrush(QColor("#00B69B")))
            elif score_val >= 80: item_score.setForeground(QBrush(QColor("#4CAF50")))
            elif score_val >= 70: item_score.setForeground(QBrush(QColor("#2962FF")))
            elif score_val >= 60: item_score.setForeground(QBrush(QColor("#FF9800")))
            else: item_score.setForeground(QBrush(QColor("#9E9E9E")))
            font_score = item_score.font()
            font_score.setBold(True)
            item_score.setFont(font_score)
            self.setItem(row, 6, item_score)
            
            # 7 Confidence
            try: conf = float(r.get("Confidence", 0))
            except: conf = 0.0
            conf_display = f"{conf:.1f}%" if conf > 0 else "--"
            item_conf = create_item(conf_display, data=conf)
            if conf >= 90: item_conf.setForeground(QBrush(QColor("#00B69B")))
            elif conf >= 75: item_conf.setForeground(QBrush(QColor("#CDDC39")))
            elif conf >= 60: item_conf.setForeground(QBrush(QColor("#F1C40F")))
            elif conf > 0: item_conf.setForeground(QBrush(QColor("#F9322C")))
            self.setItem(row, 7, item_conf)
            
            # 8 Entry
            try: entry = float(r.get("Entry", 0))
            except: entry = 0.0
            self.setItem(row, 8, create_item(f"{entry:.2f}" if entry else "--", data=entry))
            
            # 9 SL
            try: sl = float(r.get("Stop Loss", 0))
            except: sl = 0.0
            self.setItem(row, 9, create_item(f"{sl:.2f}" if sl else "--", data=sl))
            
            # 10 Target
            try: tgt = float(r.get("Target 1", 0))
            except: tgt = 0.0
            self.setItem(row, 10, create_item(f"{tgt:.2f}" if tgt else "--", data=tgt))
            
            # 11 RR
            rr = str(r.get("Risk Reward", r.get("RR", "--")))
            if not rr or rr in ("N/A", "None", "", "0", "0.0"): rr = "--"
            rr_item = create_item(rr)
            if "1:" in rr:
                try:
                    val = float(rr.split(":")[1])
                    if val >= 3: rr_item.setForeground(QBrush(QColor("#00B69B")))
                    elif val >= 2: rr_item.setForeground(QBrush(QColor("#2962FF")))
                    elif val >= 1.5: rr_item.setForeground(QBrush(QColor("#F1C40F")))
                except: pass
            self.setItem(row, 11, rr_item)
            
            # 12 Volume
            vol = str(r.get("Volume", "--"))
            if vol and vol.isdigit():
                vol_int = int(vol)
                if vol_int > 1000000:
                    vol = f"{vol_int/1000000:.1f}M"
                elif vol_int > 1000:
                    vol = f"{vol_int/1000:.1f}K"
            self.setItem(row, 12, create_item(vol, data=r.get("Volume")))
            
            # 13 Last Price
            try: lp = float(r.get("Price", r.get("Last Price", 0)))
            except: lp = 0.0
            self.setItem(row, 13, create_item(f"{lp:.2f}" if lp else "--", data=lp))
            
            # 14 Change %
            try: chg = float(r.get("Change %", r.get("Change", 0)))
            except: chg = 0.0
            chg_item = create_item(f"{chg:+.2f}%" if chg != 0 else "--", data=chg)
            if chg > 0: chg_item.setForeground(QBrush(QColor("#00B69B")))
            elif chg < 0: chg_item.setForeground(QBrush(QColor("#F9322C")))
            self.setItem(row, 14, chg_item)
            
            # 15 Reasons
            reasons = r.get("_why_selected", [])
            if isinstance(reasons, list) and reasons:
                # Remove checkmarks if they exist in the UI for space, or join with commas
                r_text = ", ".join([str(res).replace("✓ ", "") for res in reasons])
            else:
                r_text = "--"
            self.setItem(row, 15, create_item(r_text, align=Qt.AlignLeft | Qt.AlignVCenter))
            
        self.setSortingEnabled(True)
