import logging
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

class ContextMenuBuilder:
    @staticmethod
    def build_table_context_menu(parent, table, pos, main_window):
        item = table.itemAt(pos)
        if not item:
            return
            
        row = item.row()
        
        symbol = None
        
        # 1. Best attempt: Check if the full data dictionary is stored in col 0 (ScannerResultsTable convention)
        try:
            it = table.item(row, 0)
            if it:
                user_data = it.data(Qt.UserRole)
                if isinstance(user_data, dict) and "Symbol" in user_data:
                    symbol = user_data["Symbol"]
        except Exception as _e:
            logging.getLogger(__name__).debug("Suppressed exception in context_menu.py:23: %s", _e)
            
        # 2. Heuristic fallback (find .NS explicitly)
        if not symbol:
            for col in range(table.columnCount()):
                it = table.item(row, col)
                if it and ".NS" in it.text():
                    symbol = it.text().strip()
                    break
        
        # 3. Final fallback
        if not symbol:
            if table.columnCount() > 0:
                symbol = table.item(row, 0).text().strip()
                
        menu = QMenu(parent)
        
        # Option Chain Specific Logic
        is_option_chain = (table.columnCount() > 10 and table.horizontalHeaderItem(9) and "Strike" in table.horizontalHeaderItem(9).text())
        
        if is_option_chain:
            try:
                strike = table.item(row, 9).text()
                is_ce = (item.column() < 9)
                opt_type = "CE" if is_ce else "PE"
                
                # Fetch index symbol from combo box if available, otherwise generic
                parent_widget = table.parent()
                index_sym = "NIFTY"
                if hasattr(parent_widget, "combo_index"):
                    index_sym = parent_widget.combo_index.currentText()
                
                opt_sym = f"{index_sym} {strike} {opt_type}"
                
                act_chart = QAction(f"📈 Open Chart for {opt_sym}", parent)
                act_chart.triggered.connect(lambda: main_window.navigate_to_chart(opt_sym))
                menu.addAction(act_chart)
                
                act_copy_strike = QAction(f"📋 Copy Strike ({strike})", parent)
                act_copy_strike.triggered.connect(lambda: QApplication.clipboard().setText(strike))
                menu.addAction(act_copy_strike)
                
                act_copy_opt = QAction(f"📋 Copy Option Symbol ({opt_sym})", parent)
                act_copy_opt.triggered.connect(lambda: QApplication.clipboard().setText(opt_sym))
                menu.addAction(act_copy_opt)
                
                menu.addSeparator()
                
                act_alert = QAction(f"🔔 Create Alert for {opt_sym}", parent)
                menu.addAction(act_alert)
                
                act_paper = QAction(f"💼 Paper Trade {opt_sym}", parent)
                menu.addAction(act_paper)
                
            except Exception as _e:
                logging.getLogger(__name__).debug("Suppressed exception in context_menu.py:78: %s", _e)
        else:
            # Standard Table Logic
            act_chart = QAction(f"📈 Open Chart for {symbol}", parent)
            act_chart.triggered.connect(lambda: main_window.navigate_to_chart(symbol))
            menu.addAction(act_chart)
            
            menu.addSeparator()
            
            act_watch = QAction(f"⭐ Add {symbol} to Watchlist", parent)
            act_watch.triggered.connect(lambda: main_window.add_to_watchlist(symbol))
            menu.addAction(act_watch)
            
            act_copy = QAction(f"📋 Copy Symbol", parent)
            from PySide6.QtWidgets import QApplication
            act_copy.triggered.connect(lambda: QApplication.clipboard().setText(symbol))
            menu.addAction(act_copy)
            
        menu.exec_(table.viewport().mapToGlobal(pos))
