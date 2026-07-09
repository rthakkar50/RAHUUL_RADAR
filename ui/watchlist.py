"""
Watchlist Screen — save and manage favourite F&O stocks.
Supports adding, removing stocks and launching scan directly on watchlist.
"""
import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QMessageBox, QFrame,
    QCompleter
)
from PySide6.QtCore import Qt, Signal, QStringListModel
from PySide6.QtGui import QFont

import sqlite3

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "radar.db")

def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS watchlist (symbol TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

init_db()
# ── Full NSE F&O suggestion list — Symbol: Company Name ─────────────────────
_FNO_SUGGESTIONS = {
    "HDFCBANK": "HDFC Bank Ltd.",
    "ICICIBANK": "ICICI Bank Ltd.",
    "AXISBANK": "Axis Bank Ltd.",
    "KOTAKBANK": "Kotak Mahindra Bank Ltd.",
    "INDUSINDBK": "IndusInd Bank Ltd.",
    "SBIN": "State Bank of India",
    "BANKBARODA": "Bank of Baroda",
    "PNB": "Punjab National Bank",
    "CANBK": "Canara Bank",
    "FEDERALBNK": "Federal Bank Ltd.",
    "INFY": "Infosys Ltd.",
    "TCS": "Tata Consultancy Services Ltd.",
    "HCLTECH": "HCL Technologies Ltd.",
    "WIPRO": "Wipro Ltd.",
    "TECHM": "Tech Mahindra Ltd.",
    "LTI": "LTIMindtree Ltd.",
    "MPHASIS": "Mphasis Ltd.",
    "PERSISTENT": "Persistent Systems Ltd.",
    "MARUTI": "Maruti Suzuki India Ltd.",
    "MM": "Mahindra & Mahindra Ltd.",
    "TMCV": "Tata Motors Ltd.",
    "BAJAJ-AUTO": "Bajaj Auto Ltd.",
    "EICHERMOT": "Eicher Motors Ltd.",
    "HEROMOTOCO": "Hero MotoCorp Ltd.",
    "TVSMOTOR": "TVS Motor Company Ltd.",
    "SUNPHARMA": "Sun Pharmaceutical Industries Ltd.",
    "DRREDDY": "Dr. Reddy's Laboratories Ltd.",
    "CIPLA": "Cipla Ltd.",
    "DIVISLAB": "Divi's Laboratories Ltd.",
    "LUPIN": "Lupin Ltd.",
    "AUROPHARMA": "Aurobindo Pharma Ltd.",
    "ALKEM": "Alkem Laboratories Ltd.",
    "TATASTEEL": "Tata Steel Ltd.",
    "JSWSTEEL": "JSW Steel Ltd.",
    "HINDALCO": "Hindalco Industries Ltd.",
    "VEDL": "Vedanta Ltd.",
    "NMDC": "NMDC Ltd.",
    "SAIL": "Steel Authority of India Ltd.",
    "DLF": "DLF Ltd.",
    "GODREJPROP": "Godrej Properties Ltd.",
    "OBEROIRLTY": "Oberoi Realty Ltd.",
    "LODHA": "Macrotech Developers Ltd.",
    "PRESTIGE": "Prestige Estates Projects Ltd.",
    "ITC": "ITC Ltd.",
    "HUL": "Hindustan Unilever Ltd.",
    "NESTLEIND": "Nestle India Ltd.",
    "TATACONSUM": "Tata Consumer Products Ltd.",
    "BRITANNIA": "Britannia Industries Ltd.",
    "DABUR": "Dabur India Ltd.",
    "MARICO": "Marico Ltd.",
    "RELIANCE": "Reliance Industries Ltd.",
    "TATAPOWER": "Tata Power Company Ltd.",
    "ADANIENT": "Adani Enterprises Ltd.",
    "ADANIPORTS": "Adani Ports & SEZ Ltd.",
    "BPCL": "Bharat Petroleum Corporation Ltd.",
    "ONGC": "Oil & Natural Gas Corporation Ltd.",
    "NTPC": "NTPC Ltd.",
    "POWERGRID": "Power Grid Corporation of India Ltd.",
    "COALINDIA": "Coal India Ltd.",
    "GAIL": "GAIL (India) Ltd.",
    "IOC": "Indian Oil Corporation Ltd.",
    "BAJFINANCE": "Bajaj Finance Ltd.",
    "BAJAJFINSV": "Bajaj Finserv Ltd.",
    "CHOLAFIN": "Cholamandalam Investment & Finance Co.",
    "SHRIRAMFIN": "Shriram Finance Ltd.",
    "HDFCLIFE": "HDFC Life Insurance Co Ltd.",
    "SBILIFE": "SBI Life Insurance Company Ltd.",
    "ICICIPRULI": "ICICI Prudential Life Insurance Co.",
    "MUTHOOTFIN": "Muthoot Finance Ltd.",
    "NIFTY": "Nifty 50 Index",
    "BANKNIFTY": "Bank Nifty Index",
    "FINNIFTY": "Fin Nifty Index",
    "MIDCPNIFTY": "Midcap Nifty Index",
    "LTIM": "LTIMindtree Ltd.",
    "TITAN": "Titan Company Ltd.",
    "ASIANPAINT": "Asian Paints Ltd.",
    "ULTRACEMCO": "UltraTech Cement Ltd.",
    "GRASIM": "Grasim Industries Ltd.",
    "BHARTIARTL": "Bharti Airtel Ltd.",
    "ZOMATO": "Zomato Ltd.",
    "PAYTM": "One97 Communications Ltd.",
    "NYKAA": "FSN E-Commerce Ventures Ltd.",
    "IRCTC": "Indian Railway Catering & Tourism Corp.",
    "HAL": "Hindustan Aeronautics Ltd.",
    "BEL": "Bharat Electronics Ltd.",
    "BHEL": "Bharat Heavy Electricals Ltd.",
    "RVNL": "Rail Vikas Nigam Ltd.",
    "IRFC": "Indian Railway Finance Corporation Ltd.",
    "YESBANK": "Yes Bank Ltd.",
    "IDFCFIRSTB": "IDFC First Bank Ltd.",
    "RBLBANK": "RBL Bank Ltd.",
    "TRENT": "Trent Ltd.",
    "VOLTAS": "Voltas Ltd.",
    "HAVELLS": "Havells India Ltd.",
    "DIXON": "Dixon Technologies India Ltd.",
    "AMBER": "Amber Enterprises India Ltd.",
    "DMART": "Avenue Supermarts Ltd.",
    "NAUKRI": "Info Edge (India) Ltd.",
    "INDIGO": "InterGlobe Aviation Ltd.",
    "SPICEJET": "SpiceJet Ltd.",
    "LICI": "Life Insurance Corporation of India",
    "ZYDUSLIFE": "Zydus Lifesciences Ltd.",
    "TORNTPHARM": "Torrent Pharmaceuticals Ltd.",
    "SRF": "SRF Ltd.",
    "PIIND": "PI Industries Ltd.",
    "UPL": "UPL Ltd.",
    "COFORGE": "Coforge Ltd.",
    "LTTS": "L&T Technology Services Ltd.",
}

# Build suggestion strings: "SYMBOL — Company Name"
_SUGGESTION_LIST = [f"{sym}  —  {name}" for sym, name in sorted(_FNO_SUGGESTIONS.items())]


def load_watchlist() -> list:
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT symbol FROM watchlist")
        rows = [r[0] for r in c.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print("Watchlist load error:", e)
    return []

def save_watchlist(symbols: list):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM watchlist")
        for sym in symbols:
            c.execute("INSERT INTO watchlist (symbol) VALUES (?)", (sym,))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Watchlist save error:", e)


class WatchlistScreen(QWidget):
    navigate_to_chart = Signal(str)

    def __init__(self):
        super().__init__()
        self.symbols = load_watchlist()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ── Title ──────────────────────────────────────────────────────────
        title_row = QHBoxLayout()
        title = QLabel("⭐ F&O Watchlist")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #E6EDF3;")
        sub = QLabel("Save your favourite F&O stocks for quick access")
        sub.setStyleSheet("color: #8B949E; font-size: 12px;")

        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)
        layout.addWidget(sub)

        # ── Add Stock Row ──────────────────────────────────────────────────
        add_row = QHBoxLayout()
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Type 2+ letters to search: e.g. REL, HDFC, TATA...")
        self.symbol_input.setStyleSheet("""
            QLineEdit {
                background-color: #161B22;
                border: 1px solid #30363D;
                border-radius: 4px;
                padding: 8px 12px;
                color: #E6EDF3;
                font-size: 14px;
            }
            QLineEdit:focus { border-color: #58A6FF; }
        """)
        self.symbol_input.returnPressed.connect(self.add_symbol)

        self._completer_model = QStringListModel(_SUGGESTION_LIST)
        completer = QCompleter(self._completer_model, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)   # match anywhere in string
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setMaxVisibleItems(8)
        completer.popup().setStyleSheet("""
            QListView {
                background-color: #161B22;
                color: #E6EDF3;
                border: 1px solid #30363D;
                border-radius: 4px;
                font-size: 13px;
                selection-background-color: #21262D;
                selection-color: #FFFFFF;
                padding: 4px;
            }
            QListView::item {
                padding: 6px 12px;
                border-bottom: 1px solid #30363D;
            }
        """)
        # When user picks a suggestion, extract only the SYMBOL part
        completer.activated.connect(self._on_suggestion_selected)
        self.symbol_input.setCompleter(completer)

        btn_add = QPushButton("➕ Add")
        btn_add.setStyleSheet(
            "background-color: #238636; color: white; font-weight: bold; "
            "border: none; padding: 8px 16px; border-radius: 4px;"
        )
        btn_add.clicked.connect(self.add_symbol)

        add_row.addWidget(self.symbol_input)
        add_row.addWidget(btn_add)
        layout.addLayout(add_row)

        # ── List ───────────────────────────────────────────────────────────
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            QFrame {
                background-color: #0D1117;
                border: 1px solid #30363D;
                border-radius: 8px;
            }
        """)
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(0, 0, 0, 0)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                color: #E6EDF3;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px 16px;
                border-bottom: 1px solid #30363D;
            }
            QListWidget::item:selected {
                background-color: #1F6FEB;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #21262D;
            }
        """)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_click)
        list_layout.addWidget(self.list_widget)
        layout.addWidget(list_frame)

        # ── Action Buttons ─────────────────────────────────────────────────
        action_row = QHBoxLayout()

        btn_remove = QPushButton("🗑️ Remove Selected")
        btn_remove.setStyleSheet(
            "background-color: #DA3633; color: white; font-weight: bold; "
            "border: none; padding: 8px 16px; border-radius: 4px;"
        )
        btn_remove.clicked.connect(self.remove_selected)

        btn_chart = QPushButton("📈 Open Chart")
        btn_chart.setStyleSheet(
            "background-color: #1F6FEB; color: white; font-weight: bold; "
            "border: none; padding: 8px 16px; border-radius: 4px;"
        )
        btn_chart.clicked.connect(self.open_selected_chart)

        btn_clear = QPushButton("Clear All")
        btn_clear.setStyleSheet(
            "background-color: #21262D; color: white; font-weight: bold; "
            "border: 1px solid #30363D; padding: 8px 16px; border-radius: 4px;"
        )
        btn_clear.clicked.connect(self.clear_all)

        count_lbl_wrapper = QHBoxLayout()
        self.count_lbl = QLabel()
        self.count_lbl.setStyleSheet("color: #8B949E; font-size: 12px;")
        count_lbl_wrapper.addWidget(self.count_lbl)
        count_lbl_wrapper.addStretch()

        action_row.addWidget(btn_remove)
        action_row.addWidget(btn_chart)
        action_row.addStretch()
        action_row.addWidget(btn_clear)
        layout.addLayout(action_row)

        # ── Tip ────────────────────────────────────────────────────────────
        tip = QLabel("💡 Double-click a symbol to open its chart. Stocks added here appear in F&O Scanner scan list.")
        tip.setStyleSheet("color: #555; font-size: 11px; font-style: italic;")
        tip.setWordWrap(True)
        layout.addWidget(tip)

        self._refresh_list()

    def _refresh_list(self):
        self.list_widget.clear()
        
        # SPRINT-74: Auto-sort Watchlist by RS Score (Highest first)
        from core.relative_strength_engine import RelativeStrengthEngine
        rs_engine = RelativeStrengthEngine()
        
        # Fetch score for each symbol and sort
        scored_symbols = []
        for sym in self.symbols:
            score = rs_engine.get_rs_data(sym).get("score", 50)
            scored_symbols.append((sym, score))
            
        scored_symbols.sort(key=lambda x: x[1], reverse=True)
        
        for sym, score in scored_symbols:
            item = QListWidgetItem(f"  📌  {sym}   [RS: {score}]")
            self.list_widget.addItem(item)
            
        self.count_lbl.setText(f"{len(self.symbols)} stocks saved")

    def showEvent(self, event):
        """Auto-reload from file every time this screen is shown."""
        self.refresh_from_file()
        super().showEvent(event)

    def refresh_from_file(self):
        """Reload watchlist from JSON file and update UI."""
        self.symbols = load_watchlist()
        self._refresh_list()


    def _on_suggestion_selected(self, text: str):
        """Extract symbol from 'SYMBOL  —  Company Name' and add directly."""
        sym = text.split("  —  ")[0].strip()
        self.add_symbol(symbol=sym)

    def add_symbol(self, symbol: str = ""):
        raw = symbol.strip() if symbol else self.symbol_input.text().strip().upper()
        if not raw:
            return
        # If user picked from completer, it may already have " — Company" — extract symbol
        if "—" in raw:
            raw = raw.split("—")[0].strip()
        # Auto-append .NS if no suffix
        if "." not in raw:
            raw = raw + ".NS"
        if raw in self.symbols:
            QMessageBox.information(self, "Watchlist", f"{raw} is already in your watchlist! ✅")
        else:
            self.symbols.append(raw)
            save_watchlist(self.symbols)
            self._refresh_list()
            self.symbol_input.clear()

    def remove_selected(self):
        items = self.list_widget.selectedItems()
        if not items:
            return
        for item in items:
            sym = item.text().replace("  📌  ", "").split("[")[0].strip()
            if sym in self.symbols:
                self.symbols.remove(sym)
        save_watchlist(self.symbols)
        self._refresh_list()

    def clear_all(self):
        if QMessageBox.question(self, "Clear All", "Remove all watchlist stocks?") == QMessageBox.Yes:
            self.symbols.clear()
            save_watchlist(self.symbols)
            self._refresh_list()

    def open_selected_chart(self):
        items = self.list_widget.selectedItems()
        if items:
            sym = items[0].text().replace("  📌  ", "").split("[")[0].strip()
            self.navigate_to_chart.emit(sym)

    def _on_item_double_click(self, item):
        sym = item.text().replace("  📌  ", "").split("[")[0].strip()
        self.navigate_to_chart.emit(sym)
