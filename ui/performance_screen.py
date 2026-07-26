"""
Performance Screen (Stage 9 & Sprint 5 Validation)
Displays Complete Performance Analytics, Win Rates by Score/Grade, and Recent Signals.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from application.database import DatabaseManager

class PerformanceScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("📈 TRADING PERFORMANCE ANALYTICS & VALIDATION")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2196F3;")
        layout.addWidget(header)

        # --- TOP PERFORMANCE ANALYTICS (9 SPRINT 5 METRICS) ---
        analytics_box = QGroupBox("Overall Performance Analytics (Completed Trades)")
        analytics_box.setStyleSheet("QGroupBox { border: 1px solid #2196F3; border-radius: 6px; font-weight: bold; color: #FFF; padding: 12px; margin-top: 5px; }")
        grid = QGridLayout(analytics_box)
        grid.setSpacing(12)

        self.card_total = self._create_stat_card("Total Trades", grid, 0, 0)
        self.card_win_rate = self._create_stat_card("Win Rate", grid, 0, 1)
        self.card_loss_rate = self._create_stat_card("Loss Rate", grid, 0, 2)

        self.card_avg_win = self._create_stat_card("Average Winner", grid, 1, 0)
        self.card_avg_loss = self._create_stat_card("Average Loser", grid, 1, 1)
        self.card_profit_factor = self._create_stat_card("Profit Factor", grid, 1, 2)

        self.card_avg_rr = self._create_stat_card("Average Risk Reward", grid, 2, 0)
        self.card_largest_win = self._create_stat_card("Largest Win", grid, 2, 1)
        self.card_largest_loss = self._create_stat_card("Largest Loss", grid, 2, 2)

        layout.addWidget(analytics_box)

        # Stats Cards Layout (By Score and Grade)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        # 1. Win Rate by Score Bracket
        score_card = self._create_card("Win Rate by Score Bracket")
        self.score_table = self._create_stats_table(["Score Bracket", "Total Trades", "Wins", "Win Rate"])
        score_card.layout().addWidget(self.score_table)
        stats_layout.addWidget(score_card)

        # 2. Win Rate by Quality Grade
        grade_card = self._create_card("Win Rate by Quality Grade")
        self.grade_table = self._create_stats_table(["Grade", "Total Trades", "Wins", "Win Rate"])
        grade_card.layout().addWidget(self.grade_table)
        stats_layout.addWidget(grade_card)

        layout.addLayout(stats_layout)

        # All Trades Table
        trades_label = QLabel("Recent Signals Database")
        trades_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #BBB; margin-top: 10px;")
        layout.addWidget(trades_label)

        self.trades_table = QTableWidget()
        self.trades_table.setColumnCount(8)
        self.trades_table.setHorizontalHeaderLabels([
            "Date", "Symbol", "Signal", "Category", "Score", "Grade", "Target", "Result"
        ])
        self.trades_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.trades_table.verticalHeader().setVisible(False)
        self.trades_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.trades_table.setStyleSheet("""
            QTableWidget {
                background-color: #1A1C22;
                color: white;
                border: 1px solid #3D4047;
                border-radius: 6px;
                gridline-color: #2E313A;
            }
            QHeaderView::section {
                background-color: #252832;
                color: #A0AAB5;
                font-weight: bold;
                border: none;
                padding: 6px;
            }
            QTableWidget::item { padding: 5px; }
        """)
        layout.addWidget(self.trades_table)

    def _create_stat_card(self, title, grid, r, c):
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: #1A1C22; border: 1px solid #3D4047; border-radius: 6px; padding: 10px; }")
        l = QVBoxLayout(frame)
        l.setContentsMargins(5, 5, 5, 5)
        t = QLabel(title)
        t.setStyleSheet("color: #A0AAB5; font-size: 12px; border: none;")
        t.setAlignment(Qt.AlignCenter)
        v = QLabel("No Data")
        v.setStyleSheet("color: #FFF; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;")
        v.setAlignment(Qt.AlignCenter)
        l.addWidget(t)
        l.addWidget(v)
        grid.addWidget(frame, r, c)
        return v

    def _create_card(self, title):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #22242D;
                border: 1px solid #3D4047;
                border-radius: 6px;
            }
        """)
        vbox = QVBoxLayout(card)
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFF; border: none;")
        vbox.addWidget(lbl)
        return card

    def _create_stats_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setStyleSheet("""
            QTableWidget { background-color: transparent; color: white; border: none; gridline-color: #2E313A; }
            QHeaderView::section { background-color: transparent; color: #FF9800; border: none; font-weight: bold; padding: 4px; }
        """)
        return table

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()

    def refresh_data(self):
        try:
            stats = self.db.get_performance_stats()
            
            # Populate Grade Stats
            by_grade = stats.get("by_grade", [])
            self.grade_table.setRowCount(len(by_grade))
            for i, row in enumerate(by_grade):
                grade, total, wins = row
                win_rate = (wins / total * 100.0) if total > 0 else 0.0
                self.grade_table.setItem(i, 0, QTableWidgetItem(str(grade)))
                self.grade_table.setItem(i, 1, QTableWidgetItem(str(total)))
                self.grade_table.setItem(i, 2, QTableWidgetItem(str(wins)))
                self.grade_table.setItem(i, 3, QTableWidgetItem(f"{win_rate:.1f}%"))
                self.grade_table.item(i, 3).setForeground(QBrush(QColor("#4CAF50" if win_rate >= 50 else "#FF9800")))

            # Populate Score Stats
            by_score = stats.get("by_score", [])
            self.score_table.setRowCount(len(by_score))
            for i, row in enumerate(by_score):
                bracket, total, wins = row
                win_rate = (wins / total * 100.0) if total > 0 else 0.0
                self.score_table.setItem(i, 0, QTableWidgetItem(str(bracket)))
                self.score_table.setItem(i, 1, QTableWidgetItem(str(total)))
                self.score_table.setItem(i, 2, QTableWidgetItem(str(wins)))
                self.score_table.setItem(i, 3, QTableWidgetItem(f"{win_rate:.1f}%"))
                self.score_table.item(i, 3).setForeground(QBrush(QColor("#4CAF50" if win_rate >= 50 else "#FF9800")))
        except Exception as e:
            print("Error loading database performance stats:", e)

        # Populate Recent Trades & compute overall analytics
        try:
            trades = self.db.get_all_trades()
            self.trades_table.setRowCount(len(trades))
            
            closed_wins = 0
            closed_losses = 0
            gross_win_pnl = 0.0
            gross_loss_pnl = 0.0
            win_pnls = []
            loss_pnls = []
            rr_vals = []
            
            for i, t in enumerate(trades):
                # t: id, date, symbol, signal, entry, sl, target, result, return_pct, score, grade, category
                _id, dt, sym, sig, entry, sl, target, res, ret_pct, score, grade, cat = t
                
                def mk(val, color=None, align=Qt.AlignCenter):
                    it = QTableWidgetItem(str(val))
                    it.setTextAlignment(align)
                    if color: it.setForeground(QBrush(QColor(color)))
                    return it

                self.trades_table.setItem(i, 0, mk(dt))
                self.trades_table.setItem(i, 1, mk(sym, align=Qt.AlignLeft|Qt.AlignVCenter))
                self.trades_table.setItem(i, 2, mk(sig, color="#4CAF50" if sig=="BUY" else "#F44336"))
                self.trades_table.setItem(i, 3, mk(cat, color="#2196F3"))
                self.trades_table.setItem(i, 4, mk(f"{float(score):.1f}" if str(score).replace(".","").isdigit() else score))
                self.trades_table.setItem(i, 5, mk(grade, color="#FF9800"))
                self.trades_table.setItem(i, 6, mk(target))
                
                res_color = "#4CAF50" if res=="WIN" else ("#F44336" if res=="LOSS" else "#FF9800")
                self.trades_table.setItem(i, 7, mk(res, color=res_color))

                # Analytics computation for closed trades
                if res in ["WIN", "LOSS"]:
                    try:
                        ent_val = float(entry)
                        tgt_val = float(target)
                        sl_val = float(sl)
                        if res == "WIN":
                            closed_wins += 1
                            w_pnl = abs(tgt_val - ent_val)
                            gross_win_pnl += w_pnl
                            win_pnls.append(w_pnl)
                        else:
                            closed_losses += 1
                            l_pnl = abs(ent_val - sl_val)
                            gross_loss_pnl += l_pnl
                            loss_pnls.append(l_pnl)

                        if sig == "BUY" and sl_val > 0 and tgt_val > 0 and ent_val != sl_val:
                            risk = abs(ent_val - sl_val)
                            reward = abs(tgt_val - ent_val)
                            if risk > 0: rr_vals.append(reward / risk)
                        elif sig in ["SELL", "SHORT"] and sl_val > 0 and tgt_val > 0 and ent_val != sl_val:
                            risk = abs(sl_val - ent_val)
                            reward = abs(ent_val - tgt_val)
                            if risk > 0: rr_vals.append(reward / risk)
                    except Exception:
                        pass

            total_closed = closed_wins + closed_losses
            if total_closed == 0:
                for lbl in [self.card_total, self.card_win_rate, self.card_loss_rate, self.card_avg_win, self.card_avg_loss, self.card_profit_factor, self.card_avg_rr, self.card_largest_win, self.card_largest_loss]:
                    lbl.setText("No Data")
                    lbl.setStyleSheet("color: #A0AAB5; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;")
            else:
                self.card_total.setText(str(total_closed))
                self.card_total.setStyleSheet("color: #FFF; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;")
                
                win_rate = (closed_wins / total_closed) * 100.0
                loss_rate = (closed_losses / total_closed) * 100.0
                self.card_win_rate.setText(f"{win_rate:.1f}%")
                self.card_win_rate.setStyleSheet("color: #4CAF50; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;")
                self.card_loss_rate.setText(f"{loss_rate:.1f}%")
                self.card_loss_rate.setStyleSheet("color: #F44336; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;")

                avg_win = gross_win_pnl / closed_wins if closed_wins > 0 else 0.0
                avg_loss = gross_loss_pnl / closed_losses if closed_losses > 0 else 0.0
                self.card_avg_win.setText(f"₹ {avg_win:,.2f}" if avg_win > 0 else "No Data")
                self.card_avg_win.setStyleSheet("color: #4CAF50; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;")
                self.card_avg_loss.setText(f"₹ {avg_loss:,.2f}" if avg_loss > 0 else "No Data")
                self.card_avg_loss.setStyleSheet("color: #F44336; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;")

                pf = (gross_win_pnl / gross_loss_pnl) if gross_loss_pnl > 0 else (99.9 if gross_win_pnl > 0 else 0.0)
                self.card_profit_factor.setText(f"{pf:.2f}" if gross_win_pnl > 0 or gross_loss_pnl > 0 else "No Data")
                self.card_profit_factor.setStyleSheet("color: #2196F3; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;")

                if rr_vals:
                    self.card_avg_rr.setText(f"1 : {sum(rr_vals)/len(rr_vals):.2f}")
                    self.card_avg_rr.setStyleSheet("color: #FF9800; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;")
                elif avg_win > 0 and avg_loss > 0:
                    self.card_avg_rr.setText(f"1 : {avg_win/avg_loss:.2f}")
                    self.card_avg_rr.setStyleSheet("color: #FF9800; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;")
                else:
                    self.card_avg_rr.setText("No Data")
                    self.card_avg_rr.setStyleSheet("color: #A0AAB5; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;")

                self.card_largest_win.setText(f"₹ {max(win_pnls):,.2f}" if win_pnls else "No Data")
                self.card_largest_win.setStyleSheet("color: #4CAF50; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;" if win_pnls else "color: #A0AAB5; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;")

                self.card_largest_loss.setText(f"₹ {max(loss_pnls):,.2f}" if loss_pnls else "No Data")
                self.card_largest_loss.setStyleSheet("color: #F44336; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;" if loss_pnls else "color: #A0AAB5; font-size: 18px; font-weight: bold; border: none; margin-top: 4px;")

        except Exception as e:
            print("Error loading recent trades in performance screen:", e)
