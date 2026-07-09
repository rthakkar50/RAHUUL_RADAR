BG_COLOR = "#0A0E17"
CARD_BG = "#131722"
TEXT_PRIMARY = "#D1D4DC"
TEXT_SECONDARY = "#787B86"
BTN_BLUE = "#2962FF"
COLOR_BUY = "#00B69B"
COLOR_WATCH = "#F1C40F"
COLOR_SELL = "#F9322C"

GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {BG_COLOR};
    color: {TEXT_PRIMARY};
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}}
QFrame#Card {{
    background-color: {CARD_BG};
    border: 1px solid #2A2E39;
    border-radius: 8px;
}}
QFrame#PremiumCard {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1A2332, stop:1 #0A0E17);
    border: 1px solid #2A2E39;
    border-radius: 10px;
}}
QLabel {{
    color: {TEXT_PRIMARY};
    background: transparent;
}}
QLabel#Secondary {{
    color: {TEXT_SECONDARY};
}}
QLabel#PremiumTitle {{
    font-size: 18px;
    font-weight: bold;
    color: #2962FF;
}}
QPushButton {{
    background-color: #2A2E39;
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
    color: #D1D4DC;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: #363A45;
}}
QPushButton:pressed {{
    background-color: #1E222D;
}}
QPushButton:disabled {{
    background-color: #131722;
    color: #434651;
}}
QPushButton[class="primary"] {{
    background-color: #2962FF;
    color: #FFFFFF;
}}
QPushButton[class="primary"]:hover {{
    background-color: #1E53E5;
}}
QPushButton[class="primary"]:pressed {{
    background-color: #0039CB;
}}
QTableWidget {{
    background-color: {CARD_BG};
    alternate-background-color: #181C27;
    border: 1px solid #2A2E39;
    gridline-color: transparent;
    color: {TEXT_PRIMARY};
    border-radius: 6px;
    font-size: 13px;
    outline: none;
}}
QTableWidget::item {{
    padding: 4px 8px;
    border-bottom: 1px solid #1E222D;
}}
QTableWidget::item:hover {{
    background-color: #1C2230;
}}
QTableWidget::item:selected {{
    background-color: rgba(41, 98, 255, 0.15);
    color: #58A6FF;
    border-top: 1px solid #2962FF;
    border-bottom: 1px solid #2962FF;
}}
QHeaderView::section {{
    background-color: {CARD_BG};
    color: {TEXT_SECONDARY};
    padding: 8px;
    border: none;
    border-bottom: 1px solid #2A2E39;
    font-weight: bold;
    font-size: 13px;
}}
QProgressBar {{
    background-color: #1E222D;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: white;
    height: 18px;
}}
QProgressBar::chunk {{
    background-color: #2962FF;
    border-radius: 4px;
}}
QTabWidget::pane {{
    border: 1px solid #2A2E39;
    background-color: {BG_COLOR};
}}
QTabBar::tab {{
    background-color: {CARD_BG};
    color: {TEXT_SECONDARY};
    padding: 10px 16px;
    border: none;
    border-bottom: 2px solid transparent;
    font-weight: 500;
    min-width: 80px;
}}
QTabBar::tab:selected {{
    color: {TEXT_PRIMARY};
    border-bottom: 2px solid #2962FF;
}}
QTabBar::tab:hover {{
    color: {TEXT_PRIMARY};
}}
QSplitter::handle {{
    background-color: #2A2E39;
    width: 2px;
}}
QStatusBar {{
    background-color: {CARD_BG};
    color: {TEXT_SECONDARY};
    border-top: 1px solid #2A2E39;
}}
"""
