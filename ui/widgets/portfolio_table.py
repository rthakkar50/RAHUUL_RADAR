from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtGui import QColor, QBrush
from PySide6.QtCore import Qt

class PortfolioTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #1A1C20;
                gridline-color: #2D3038;
                color: #FFFFFF;
                selection-background-color: #2D3A56;
                selection-color: #FFFFFF;
                border: 1px solid #3D4047;
            }
            QHeaderView::section {
                background-color: #252832;
                color: #A0AAB5;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)

    def populate(self, positions):
        self.setSortingEnabled(False)
        self.setRowCount(len(positions))
        
        headers = [
            "Symbol", "Direction", "Qty", "Entry Price", "CMP", 
            "Unrealized P/L", "Stop Loss", "Target", "R:R", "Status"
        ]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        for row, p in enumerate(positions):
            is_dict = isinstance(p, dict)
            sym = str(p.get("symbol", "") if is_dict else getattr(p, "symbol", ""))
            direction = str(p.get("direction", p.get("side", "BUY")) if is_dict else getattr(p, "direction", "BUY"))
            qty = int(p.get("quantity", p.get("qty", 0)) if is_dict else getattr(p, "qty", 0))
            entry = float(p.get("avg_entry", p.get("entry_price", 0.0)) if is_dict else getattr(p, "entry_price", 0.0))
            cmp_price = float(p.get("current_price", p.get("cmp", entry)) if is_dict else getattr(p, "current_price", entry))
            unrealized_pnl = float(p.get("overall_pnl", p.get("unrealized_pnl", (cmp_price - entry) * qty * (1 if direction=='BUY' else -1))) if is_dict else getattr(p, "unrealized_pnl", 0.0))
            sl = float(p.get("stop_loss", p.get("sl", 0.0)) if is_dict else getattr(p, "sl", 0.0))
            target = float(p.get("target", 0.0) if is_dict else getattr(p, "target", 0.0))
            status = str(p.get("status", "OPEN") if is_dict else getattr(p, "status", "OPEN"))

            # Compute R:R
            rr_str = "No Data"
            try:
                if direction == "BUY" and sl > 0 and target > 0 and entry != sl:
                    risk = abs(entry - sl)
                    reward = abs(target - entry)
                    if risk > 0 and reward > 0:
                        rr_str = f"1 : {reward/risk:.2f}"
                elif direction in ["SELL", "SHORT"] and sl > 0 and target > 0 and entry != sl:
                    risk = abs(sl - entry)
                    reward = abs(entry - target)
                    if risk > 0 and reward > 0:
                        rr_str = f"1 : {reward/risk:.2f}"
            except Exception:
                rr_str = "No Data"

            def mk_item(txt, align=Qt.AlignCenter, color=None):
                it = QTableWidgetItem(str(txt))
                it.setTextAlignment(align)
                if color: it.setForeground(QBrush(QColor(color)))
                return it

            self.setItem(row, 0, mk_item(sym))
            dir_col = "#4CAF50" if direction=="BUY" else "#F44336"
            self.setItem(row, 1, mk_item(direction, color=dir_col))
            self.setItem(row, 2, mk_item(qty))
            self.setItem(row, 3, mk_item(f"{entry:,.2f}"))
            self.setItem(row, 4, mk_item(f"{cmp_price:,.2f}"))
            
            pnl_col = "#4CAF50" if unrealized_pnl > 0 else ("#F44336" if unrealized_pnl < 0 else "#FFF")
            self.setItem(row, 5, mk_item(f"{unrealized_pnl:,.2f}", color=pnl_col))
            self.setItem(row, 6, mk_item(f"{sl:,.2f}" if sl > 0 else "No Data", color="#F44336"))
            self.setItem(row, 7, mk_item(f"{target:,.2f}" if target > 0 else "No Data", color="#4CAF50"))
            self.setItem(row, 8, mk_item(rr_str, color="#FF9800"))
            self.setItem(row, 9, mk_item(status, color="#2196F3" if status=="OPEN" else "#9E9E9E"))
            
        self.setSortingEnabled(True)
