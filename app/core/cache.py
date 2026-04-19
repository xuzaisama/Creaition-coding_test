from __future__ import annotations

from copy import deepcopy
from threading import Lock
from time import monotonic
from typing import Generic, TypeVar

from app.core.config import settings

T = TypeVar("T")


class TTLCache(Generic[T]):
    """A small in-memory TTL cache suitable for single-process development."""

    def __init__(self, default_ttl_seconds: int = 60) -> None:
        self.default_ttl_seconds = default_ttl_seconds
        self._store: dict[str, tuple[float, T]] = {}
        self._lock = Lock()

    def get(self, key: str) -> T | None:
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None

            expires_at, value = item
            if expires_at <= monotonic():
                # Expired entries are removed lazily on access to keep the cache simple.
                self._store.pop(key, None)
                return None

            # Return a copy so cached payloads cannot be mutated by callers.
            return deepcopy(value)

    def set(self, key: str, value: T, ttl_seconds: int | None = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
        with self._lock:
            self._store[key] = (monotonic() + ttl, deepcopy(value))

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def invalidate_prefix(self, prefix: str) -> None:
        with self._lock:
            keys = [key for key in self._store if key.startswith(prefix)]
            for key in keys:
                self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


task_cache: TTLCache[dict] = TTLCache(default_ttl_seconds=settings.cache_ttl_seconds)
