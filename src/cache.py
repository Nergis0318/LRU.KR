import asyncio
from collections import OrderedDict
from typing import Optional


class AsyncLRUCache:
    """Thread-safe async LRU cache for URL redirects"""

    def __init__(self, maxsize: int = 10000):
        self._cache: OrderedDict[str, str] = OrderedDict()
        self._maxsize = maxsize
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache, moving it to end (most recently used)"""
        async with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
            return None

    async def set(self, key: str, value: str):
        """Set value in cache, evicting oldest if at capacity"""
        async with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self._maxsize:
                    self._cache.popitem(last=False)
                self._cache[key] = value

    async def clear(self):
        """Clear all entries from cache"""
        async with self._lock:
            self._cache.clear()

    async def size(self) -> int:
        """Get current cache size"""
        async with self._lock:
            return len(self._cache)
