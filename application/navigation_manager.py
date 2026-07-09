import threading
from PySide6.QtCore import QObject, Signal

class NavigationManager(QObject):
    """
    Global Navigation Manager for RAHUUL RADAR PRO.
    Allows any component to request navigation to a specific page
    without needing a direct reference to the MainWindow.
    """
    
    # Signal emitted when a navigation request is made
    # payload can contain extra info like symbol="RELIANCE"
    navigation_requested = Signal(str, dict)

    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(NavigationManager, cls).__new__(cls, *args, **kwargs)
                QObject.__init__(cls._instance)
            return cls._instance
            
    def __init__(self):
        # Prevent re-initialization since it's a singleton
        pass

    @classmethod
    def navigate_to(cls, page_name: str, **kwargs):
        """
        Navigate to a specific page.
        Example: NavigationManager.navigate_to("Charts", symbol="RELIANCE.NS")
        """
        instance = cls()
        instance.navigation_requested.emit(page_name, kwargs)
