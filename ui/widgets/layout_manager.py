import logging

class LayoutManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def apply_geometry(self, widget, geometry_data):
        self.logger.info("Applied mock geometry")
