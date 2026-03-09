from __future__ import annotations

import threading
import time
from typing import Any


class TTLCache:
    def __init__(self, ttl_seconds: int, max_entries: int = 256) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._store: dict[Any, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: Any) -> Any | None:
        now = time.time()
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None

            expires_at, value = item
            if now >= expires_at:
                self._store.pop(key, None)
                return None
            return value

    def set(self, key: Any, value: Any) -> None:
        now = time.time()
        expires_at = now + self.ttl_seconds
        with self._lock:
            if len(self._store) >= self.max_entries:
                self._evict_expired(now)
                if len(self._store) >= self.max_entries:
                    oldest_key = min(self._store.items(), key=lambda entry: entry[1][0])[0]
                    self._store.pop(oldest_key, None)

            self._store[key] = (expires_at, value)

    def _evict_expired(self, now: float) -> None:
        for key, (expires_at, _) in list(self._store.items()):
            if now >= expires_at:
                self._store.pop(key, None)
