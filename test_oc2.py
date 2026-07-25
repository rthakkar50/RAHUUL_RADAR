import sys
from PySide6.QtWidgets import QApplication
from ui.option_chain_page import OptionChainPage

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)
    
try:
    page = OptionChainPage()
    print("OptionChainPage Phase 2 loaded successfully.")
    sys.exit(0)
except Exception as e:
    import traceback
    print("Failed to load OptionChainPage:")
    traceback.print_exc()
    sys.exit(1)
