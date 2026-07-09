"""
RAHUUL_RADAR
Professional Indian Stock Market Scanner (GUI Edition)
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import get_logger

logger = get_logger(__name__)

def run_self_test():
    print("====================================")
    print("RUNNING SELF-TEST (SPRINT-70)")
    
    # 1. Database
    import sqlite3
    import os
    
    # Verify Databases
    db_checks = {
        "radar.db": ["watchlist"],
        "trade_journal.db": ["trades"],
        "paper_trading.db": ["positions", "portfolio"]
    }
    
    for db_name, tables in db_checks.items():
        db_path = f"data/{db_name}"
        if not os.path.exists(db_path):
            print(f"[WARN] Database {db_name} does not exist yet.")
            continue
            
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            for t in tables:
                c.execute(f"SELECT 1 FROM {t} LIMIT 1")
            conn.close()
            print(f"[PASS] Database: {db_name}")
        except Exception as e:
            print(f"[FAIL] Database {db_name} - {e}")
        
    # 2. Providers
    try:
        from application.data_manager import DataManager
        dm = DataManager.get_instance()
        print("[PASS] Providers & DataManager")
    except Exception as e:
        print(f"[FAIL] Providers: {e}")
        
    # 3. Config
    try:
        from config.config import AppConfig
        cfg = AppConfig()
        print("[PASS] Configuration")
    except Exception as e:
        print(f"[FAIL] Configuration: {e}")
        
    print("====================================")
    
def patch_qtablewidget():
    from PySide6.QtWidgets import QTableWidget
    from PySide6.QtCore import Qt
    from utils.context_menu import ContextMenuBuilder
    
    original_init = QTableWidget.__init__
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # We need a reference to main_window to navigate
        # A hacky way is to get the top level widget
        def show_menu(pos):
            top_level = self.window()
            ContextMenuBuilder.build_table_context_menu(self, self, pos, top_level)
            
        self.customContextMenuRequested.connect(show_menu)
        
    QTableWidget.__init__ = new_init

def main():
    logger.info("====================================")
    logger.info("Application Start")
    
    # Run Pre-flight
    run_self_test()
    patch_qtablewidget()
    
    logger.info("Initializing RAHUUL RADAR Desktop UI...")
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nApplication interrupted by user.")
        logger.info("Application Close")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal unhandled error occurred: {e}")
        logger.info("Application Close")
        sys.exit(1)
    finally:
        logger.info("Application Close")
