import time
from typing import Any, Optional, Dict

class SimpleCache:
    def __init__(self, default_ttl: int = 300):
        # default TTL in seconds (5 minutes)
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        item = self._cache.get(key)
        if not item:
            return None
        if time.time() > item['expires_at']:
            del self._cache[key]
            return None
        return item['value']

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        duration = ttl if ttl is not None else self.default_ttl
        self._cache[key] = {
            'value': value,
            'expires_at': time.time() + duration
        }

    def clear(self) -> None:
        self._cache.clear()

cache = SimpleCache(default_ttl=600)  # 10 minutes cache
