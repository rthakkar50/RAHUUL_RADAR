from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from ui.widgets.watchlist_toolbar import WatchlistToolbar
from ui.widgets.watchlist_table import WatchlistTable
from application.watchlist_service import WatchlistService

class WatchlistPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = WatchlistService()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Top Bar
        top_bar = QHBoxLayout()
        title = QLabel("Watchlist Manager")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        top_bar.addWidget(title)
        top_bar.addStretch()
        
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.refresh_data)
        top_bar.addWidget(btn_refresh)
        self.layout.addLayout(top_bar)
        
        # Toolbar
        self.toolbar = WatchlistToolbar()
        self.layout.addWidget(self.toolbar)
        
        # Table
        self.table = WatchlistTable()
        self.layout.addWidget(self.table)
        
        # Empty State Overlay
        self.lbl_empty = QLabel("No stocks in Watchlist", self.table)
        self.lbl_empty.setStyleSheet("font-size: 16px; color: #888; font-weight: bold; background-color: transparent;")
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.lbl_empty.hide()
        
        self.refresh_data()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'lbl_empty'):
            self.lbl_empty.resize(self.table.size())
            
    def refresh_data(self):
        results = self.service.get_watchlist()
        self.table.populate(results)
        
        if len(results) == 0:
            self.lbl_empty.show()
        else:
            self.lbl_empty.hide()
