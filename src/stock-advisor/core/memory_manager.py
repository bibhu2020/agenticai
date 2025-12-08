# core/memory_manager.py
import json
from pathlib import Path

class MemoryManager:
    def __init__(self, cache_file: str = "cache.json"):
        self.cache_file = Path(cache_file)
        if not self.cache_file.exists():
            self._write_cache({"analysis": {}, "portfolio": {}})

    def _read_cache(self):
        with open(self.cache_file, "r") as f:
            return json.load(f)

    def _write_cache(self, data):
        with open(self.cache_file, "w") as f:
            json.dump(data, f, indent=4)

    def save_analysis(self, symbol: str, analysis: dict):
        cache = self._read_cache()
        cache["analysis"][symbol] = analysis
        self._write_cache(cache)

    def get_analysis(self, symbol: str):
        cache = self._read_cache()
        return cache["analysis"].get(symbol)

    def save_portfolio(self, portfolio_data: dict):
        cache = self._read_cache()
        cache["portfolio"] = portfolio_data
        self._write_cache(cache)

    def get_portfolio(self):
        cache = self._read_cache()
        portfolio = cache.get("portfolio")
        return portfolio if portfolio else None


    def clear_cache(self):
        self._write_cache({"analysis": {}, "portfolio": {}})
