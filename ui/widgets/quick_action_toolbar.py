from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
    QLineEdit, QComboBox, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ui.styles import CARD_BG, BTN_BLUE, COLOR_WATCH

class QuickActionToolbar(QFrame):
    # Signals to communicate with the main page
    action_requested = Signal(str)
    search_changed = Signal(str)
    filter_changed = Signal(str)
    sort_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{ background-color: {CARD_BG}; border-radius: 6px; border: 1px solid #2A2E39; }}
            QLineEdit, QComboBox {{ 
                background-color: #181C27; color: white; border: 1px solid #2A2E39; 
                padding: 6px 10px; border-radius: 4px; height: 20px; font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus {{ border: 1px solid #2962FF; }}
            QLabel {{ color: #787B86; font-size: 12px; font-weight: 500; }}
            QComboBox::drop-down {{ border: none; }}
        """)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Top Row: Mode, Timeframe, Sector, Score
        top_row = QHBoxLayout()
        top_row.setSpacing(15)
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(15)
        
        # Mode
        lbl_mode = QLabel("Mode:")
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Swing", "Intraday"])
        self.combo_mode.setFixedWidth(100)
        top_row.addWidget(lbl_mode)
        top_row.addWidget(self.combo_mode)
        
        # Timeframe
        lbl_timeframe = QLabel("Timeframe:")
        self.combo_timeframe = QComboBox()
        self.combo_timeframe.addItems(["1 Day", "1 Week", "1 Month", "1 Hour", "15 Min", "5 Min"])
        self.combo_timeframe.setFixedWidth(100)
        top_row.addWidget(lbl_timeframe)
        top_row.addWidget(self.combo_timeframe)
        
        # Sector Filter
        lbl_sector = QLabel("Sector:")
        self.combo_sector = QComboBox()
        self.combo_sector.addItems(["All Sectors", "IT", "Banking", "Energy", "Auto", "Pharma", "FMCG"])
        self.combo_sector.setFixedWidth(110)
        self.combo_sector.currentTextChanged.connect(self.filter_changed.emit)
        top_row.addWidget(lbl_sector)
        top_row.addWidget(self.combo_sector)
        
        # Score Filter
        lbl_score = QLabel("Score:")
        self.combo_score = QComboBox()
        self.combo_score.addItems(["All Scores", "Elite (>90)", "Strong (>80)", "Good (>70)"])
        self.combo_score.setFixedWidth(110)
        self.combo_score.currentTextChanged.connect(self.filter_changed.emit)
        top_row.addWidget(lbl_score)
        top_row.addWidget(self.combo_score)
        
        top_row.addStretch()
        
        # Actions and Exports inline
        self.btn_scan = QPushButton("Scan Now")
        self.btn_scan.setProperty("class", "primary")
        
        self.btn_csv = QPushButton("CSV")
        self.btn_excel = QPushButton("Excel")
        self.btn_json = QPushButton("JSON")
        
        self.lbl_selected = QLabel("0 Selected")
        self.lbl_selected.setStyleSheet("color: #2962FF; font-weight: bold; font-size: 12px; margin-left: 10px;")
        
        self.btn_copy = QPushButton("Copy Symbol")
        self.btn_analysis = QPushButton("Analysis")
        
        self.selection_buttons = [self.btn_copy, self.btn_analysis]
        for btn in self.selection_buttons:
            btn.setEnabled(False)
            
        bottom_row.addWidget(self.btn_scan)
        bottom_row.addWidget(QLabel(" | "))
        bottom_row.addWidget(self.btn_csv)
        bottom_row.addWidget(self.btn_excel)
        bottom_row.addWidget(self.btn_json)
        
        bottom_row.addWidget(self.lbl_selected)
        bottom_row.addWidget(self.btn_copy)
        bottom_row.addWidget(self.btn_analysis)
        
        bottom_row.addStretch()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Symbol...")
        self.search_input.setFixedWidth(180)
        self.search_input.textChanged.connect(self.search_changed.emit)
        bottom_row.addWidget(self.search_input)
        
        main_layout.addLayout(top_row)
        main_layout.addLayout(bottom_row)


        # Connect internal buttons to generic action router
        self.btn_scan.clicked.connect(lambda: self.action_requested.emit("scan"))
        self.btn_csv.clicked.connect(lambda: self.action_requested.emit("export_csv"))
        self.btn_json.clicked.connect(lambda: self.action_requested.emit("export_json"))
        self.btn_excel.clicked.connect(lambda: self.action_requested.emit("export_excel"))
        self.btn_copy.clicked.connect(lambda: self.action_requested.emit("copy_symbol"))
        self.btn_analysis.clicked.connect(lambda: self.action_requested.emit("open_analysis"))

    def update_selection_count(self, count: int):
        self.lbl_selected.setText(f"{count} Selected")
        for btn in self.selection_buttons:
            btn.setEnabled(count > 0)
            
        # Disable singular actions if multiple selected
        if count > 1:
            self.btn_analysis.setEnabled(False)

    def update_status(self, time_str, exec_t, market_quality):
        pass # To be implemented if we want to show it on toolbar
