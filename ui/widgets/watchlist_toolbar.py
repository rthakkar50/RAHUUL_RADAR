from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLineEdit

class WatchlistToolbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search Favorites...")
        self.btn_add = QPushButton("Add")
        self.layout.addWidget(self.search)
        self.layout.addWidget(self.btn_add)
