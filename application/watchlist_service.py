import json
import os
import logging
from typing import Dict, List, Any
import datetime

logger = logging.getLogger(__name__)

WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "watchlist.json")

class WatchlistService:
    def __init__(self):
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(WATCHLIST_FILE):
            os.makedirs(os.path.dirname(WATCHLIST_FILE), exist_ok=True)
            return self._default_schema()
        try:
            with open(WATCHLIST_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load watchlist: {e}")
            return self._default_schema()

    def _default_schema(self) -> Dict[str, Any]:
        return {
            "lists": {
                "Default": [],
                "Swing": [],
                "Intraday": [],
                "Scalping": []
            },
            "pinned": [],
            "metadata": {} # symbol -> {tag, notes, last_updated}
        }

    def _save(self):
        try:
            with open(WATCHLIST_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save watchlist: {e}")

    def add_symbol(self, symbol: str, list_name: str = "Default"):
        if list_name not in self.data["lists"]:
            self.data["lists"][list_name] = []
        if symbol not in self.data["lists"][list_name]:
            self.data["lists"][list_name].append(symbol)
            self._save()

    def remove_symbol(self, symbol: str, list_name: str = "Default"):
        if list_name in self.data["lists"]:
            if symbol in self.data["lists"][list_name]:
                self.data["lists"][list_name].remove(symbol)
            if symbol in self.data["pinned"]:
                self.data["pinned"].remove(symbol)
            self._save()

    def update_metadata(self, symbol: str, tag: str = None, notes: str = None):
        if symbol not in self.data["metadata"]:
            self.data["metadata"][symbol] = {}
        if tag is not None:
            self.data["metadata"][symbol]["tag"] = tag
        if notes is not None:
            self.data["metadata"][symbol]["notes"] = notes
        self._save()

    def toggle_pin(self, symbol: str):
        if symbol in self.data["pinned"]:
            self.data["pinned"].remove(symbol)
        else:
            self.data["pinned"].append(symbol)
        self._save()

    def get_watchlist(self, list_name: str = "Default") -> List[Dict[str, Any]]:
        symbols = self.data["lists"].get(list_name, [])
        pinned = [s for s in symbols if s in self.data["pinned"]]
        unpinned = [s for s in symbols if s not in self.data["pinned"]]
        
        # Return structured format
        res = []
        for s in pinned + unpinned:
            meta = self.data["metadata"].get(s, {})
            # We return empty dynamic fields, to be hydrated by sync_with_scan_results
            res.append({
                "Symbol": s,
                "Company": "N/A",
                "Sector": "N/A",
                "Signal": "WAIT",
                "Confidence": "0",
                "Price": "0",
                "Change %": "0",
                "Volume": "0",
                "Trend": "N/A",
                "Last Updated": meta.get("last_updated", "Never"),
                "Tag": meta.get("tag", "None"),
                "Notes": meta.get("notes", ""),
                "Pinned": s in self.data["pinned"]
            })
        return res

    def sync_with_scan_results(self, scan_results: List[Dict[str, Any]]):
        """Auto updates watchlist fields from a scan run in-memory"""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        updated = False
        
        # Map scan results by symbol for O(1) lookup
        scan_map = {r["Symbol"]: r for r in scan_results}
        
        for symbol, meta in self.data["metadata"].items():
            if symbol in scan_map:
                meta["last_updated"] = now
                meta["_cached_scan"] = scan_map[symbol]
                updated = True
                
        if updated:
            self._save()
