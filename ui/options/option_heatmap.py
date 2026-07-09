from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt, QRect

class OptionHeatmapWidget(QWidget):
    """
    A visual component that maps Open Interest density across strikes.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.calls_data = [] # List of tuples (strike, oi_normalized)
        self.puts_data = []
        self.max_pain = 0.0
        
    def update_data(self, calls, puts, max_pain):
        """
        calls/puts: list of (strike, open_interest)
        """
        if not calls and not puts:
            return
            
        max_oi = max([oi for _, oi in calls] + [oi for _, oi in puts]) if calls or puts else 1
        self.calls_data = [(s, oi / max_oi) for s, oi in calls]
        self.puts_data = [(s, oi / max_oi) for s, oi in puts]
        self.max_pain = max_pain
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Draw background
        painter.fillRect(0, 0, w, h, QColor("#111111"))
        
        if not self.calls_data and not self.puts_data:
            painter.setPen(Qt.white)
            painter.drawText(self.rect(), Qt.AlignCenter, "No Option Chain Data")
            return
            
        # Simplistic rendering mapping strikes along X axis
        all_strikes = sorted(list(set([s for s, _ in self.calls_data] + [s for s, _ in self.puts_data])))
        if not all_strikes:
            return
            
        min_s = all_strikes[0]
        max_s = all_strikes[-1]
        range_s = max_s - min_s if max_s > min_s else 1
        
        # Draw Calls (Red-ish) and Puts (Green-ish)
        for s, norm_oi in self.calls_data:
            x = int(((s - min_s) / range_s) * w)
            bar_h = int(norm_oi * (h / 2))
            painter.fillRect(x - 2, 0, 4, bar_h, QColor(255, 0, 0, 150))
            
        for s, norm_oi in self.puts_data:
            x = int(((s - min_s) / range_s) * w)
            bar_h = int(norm_oi * (h / 2))
            painter.fillRect(x - 2, h - bar_h, 4, bar_h, QColor(0, 255, 0, 150))
            
        # Draw Max Pain Line
        mp_x = int(((self.max_pain - min_s) / range_s) * w)
        painter.setPen(QColor(255, 255, 0)) # Yellow
        painter.drawLine(mp_x, 0, mp_x, h)
        painter.drawText(mp_x + 5, int(h/2), "Max Pain")
