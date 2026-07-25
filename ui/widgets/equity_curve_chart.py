import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from ui.styles import BG_COLOR, TEXT_PRIMARY, COLOR_BUY

class EquityCurveChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Configure pyqtgraph appearance
        pg.setConfigOption('background', BG_COLOR)
        pg.setConfigOption('foreground', TEXT_PRIMARY)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Total Equity')
        self.plot_widget.setLabel('bottom', 'Time (Updates)')
        
        self.curve = self.plot_widget.plot(pen=pg.mkPen(COLOR_BUY, width=2), fillLevel=0, brush=(0, 200, 100, 50))
        
        self.layout.addWidget(self.plot_widget)
        
        self.x_data = []
        self.y_data = []
        
    def update_data(self, history_df):
        """
        Updates the chart with equity history data.
        history_df: DataFrame with at least 'capital' column
        """
        if history_df.empty or 'capital' not in history_df.columns:
            return
            
        self.y_data = history_df['capital'].tolist()
        self.x_data = list(range(len(self.y_data)))
        
        # Calculate dynamic bounds for better visualization
        if len(self.y_data) > 0:
            min_y = min(self.y_data)
            max_y = max(self.y_data)
            padding = (max_y - min_y) * 0.1 if max_y > min_y else max_y * 0.01
            
            # Set dynamic fill level
            fill_base = min_y - padding
            self.curve.setFillLevel(fill_base)
            
            # Adjust plot limits manually if it's too flat
            if max_y == min_y:
                self.plot_widget.setYRange(min_y - min_y*0.01, min_y + min_y*0.01)
                
        self.curve.setData(self.x_data, self.y_data)
