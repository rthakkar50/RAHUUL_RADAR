import time
import logging

logger = logging.getLogger("DataManager")

class CacheManager:
    def __init__(self):
        self._cache = {}
        
    def set(self, key, data):
        self._cache[key] = {
            'timestamp': time.time(),
            'data': data
        }
        
    def get(self, key):
        if key in self._cache:
            return self._cache[key]['data']
        return None
        
    def get_all(self):
        return self._cache
