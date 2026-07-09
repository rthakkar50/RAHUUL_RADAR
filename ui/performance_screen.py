"""
Performance Screen (Stage 9)
Displays Live Validation results, Win Rates, and Score Grade Analysis.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt
from application.database import DatabaseManager

class PerformanceScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel("Performance Validation (Live DB)")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(header)

        # Stats Cards Layout
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        # 1. Win Rate by Score Bracket
        score_card = self._create_card("Win Rate by Score")
        self.score_table = self._create_stats_table(["Score Bracket", "Total Trades", "Wins", "Win Rate"])
        score_card.layout().addWidget(self.score_table)
        stats_layout.addWidget(score_card)

        # 2. Win Rate by Quality Grade
        grade_card = self._create_card("Win Rate by Grade")
        self.grade_table = self._create_stats_table(["Grade", "Total Trades", "Wins", "Win Rate"])
        grade_card.layout().addWidget(self.grade_table)
        stats_layout.addWidget(grade_card)

        layout.addLayout(stats_layout)

        # All Trades Table
        trades_label = QLabel("Recent Signals Database")
        trades_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #BBB;")
        layout.addWidget(trades_label)

        self.trades_table = QTableWidget()
        self.trades_table.setColumnCount(8)
        self.trades_table.setHorizontalHeaderLabels([
            "Date", "Symbol", "Signal", "Category", "Score", "Grade", "Target", "Result"
        ])
        self.trades_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.trades_table.setStyleSheet("""
            QTableWidget {
                background-color: #22242D;
                color: white;
                border: 1px solid #3D4047;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #1A1C23;
                color: #888;
                font-weight: bold;
                border: none;
                padding: 4px;
            }
            QTableWidget::item { padding: 4px; border-bottom: 1px solid #333; }
        """)
        layout.addWidget(self.trades_table)

    def _create_card(self, title):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #22242D;
                border: 1px solid #3D4047;
                border-radius: 8px;
            }
        """)
        vbox = QVBoxLayout(card)
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFF; border: none;")
        vbox.addWidget(lbl)
        return card

    def _create_stats_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet("""
            QTableWidget { background-color: transparent; color: white; border: none; }
            QHeaderView::section { background-color: transparent; color: #FF9800; border: none; font-weight: bold; }
        """)
        return table

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()

    def refresh_data(self):
        stats = self.db.get_performance_stats()
        
        # Populate Grade Stats
        by_grade = stats["by_grade"]
        self.grade_table.setRowCount(len(by_grade))
        for i, row in enumerate(by_grade):
            grade, total, wins = row
            win_rate = (wins / total * 100) if total > 0 else 0
            self.grade_table.setItem(i, 0, QTableWidgetItem(str(grade)))
            self.grade_table.setItem(i, 1, QTableWidgetItem(str(total)))
            self.grade_table.setItem(i, 2, QTableWidgetItem(str(wins)))
            self.grade_table.setItem(i, 3, QTableWidgetItem(f"{win_rate:.1f}%"))

        # Populate Score Stats
        by_score = stats["by_score"]
        self.score_table.setRowCount(len(by_score))
        for i, row in enumerate(by_score):
            bracket, total, wins = row
            win_rate = (wins / total * 100) if total > 0 else 0
            self.score_table.setItem(i, 0, QTableWidgetItem(str(bracket)))
            self.score_table.setItem(i, 1, QTableWidgetItem(str(total)))
            self.score_table.setItem(i, 2, QTableWidgetItem(str(wins)))
            self.score_table.setItem(i, 3, QTableWidgetItem(f"{win_rate:.1f}%"))

        # Populate Recent Trades
        trades = self.db.get_all_trades()
        self.trades_table.setRowCount(len(trades))
        for i, t in enumerate(trades):
            # t: id, date, symbol, signal, entry, sl, target, result, return_pct, score, grade, category
            self.trades_table.setItem(i, 0, QTableWidgetItem(str(t[1]))) # date
            self.trades_table.setItem(i, 1, QTableWidgetItem(str(t[2]))) # symbol
            self.trades_table.setItem(i, 2, QTableWidgetItem(str(t[3]))) # signal
            self.trades_table.setItem(i, 3, QTableWidgetItem(str(t[11]))) # category
            self.trades_table.setItem(i, 4, QTableWidgetItem(str(t[9]))) # score
            self.trades_table.setItem(i, 5, QTableWidgetItem(str(t[10]))) # grade
            self.trades_table.setItem(i, 6, QTableWidgetItem(str(t[6]))) # target
            
            # Result color coding
            res_item = QTableWidgetItem(str(t[7]))
            if t[7] == "WIN":
                res_item.setForeground(Qt.green)
            elif t[7] == "LOSS":
                res_item.setForeground(Qt.red)
            else:
                res_item.setForeground(Qt.yellow)
            self.trades_table.setItem(i, 7, res_item)
