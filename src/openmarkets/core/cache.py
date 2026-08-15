"""In-memory thread-safe TTL cache for OpenMarkets.

Provides a lightweight time-to-live caching mechanism to protect upstream
Yahoo Finance endpoints against repetitive queries and rate-limiting.
"""

from __future__ import annotations

import functools
import threading
import time
from typing import Any, Callable, TypeVar

_F = TypeVar("_F", bound=Callable[..., Any])


class TTLCache:
    """Thread-safe in-memory cache with time-to-live expiration."""

    def __init__(self, default_ttl: float = 300.0, maxsize: int = 1024) -> None:
        self._default_ttl = default_ttl
        self._maxsize = maxsize
        self._cache: dict[str, tuple[Any, float]] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Any | None:
        """Retrieve a value from the cache if present and not expired."""
        with self._lock:
            if key not in self._cache:
                return None
            value, expires_at = self._cache[key]
            if time.monotonic() > expires_at:
                del self._cache[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Store a value in the cache with a specified TTL."""
        ttl_seconds = ttl if ttl is not None else self._default_ttl
        expires_at = time.monotonic() + ttl_seconds
        with self._lock:
            if len(self._cache) >= self._maxsize and key not in self._cache:
                now = time.monotonic()
                expired_keys = [k for k, (_, exp) in self._cache.items() if now > exp]
                for k in expired_keys:
                    del self._cache[k]
                if len(self._cache) >= self._maxsize:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
            self._cache[key] = (value, expires_at)

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)


_GLOBAL_CACHE = TTLCache(default_ttl=300.0)


def get_global_cache() -> TTLCache:
    """Get the global TTL cache instance."""
    return _GLOBAL_CACHE


def _is_ignorable_arg(obj: Any) -> bool:
    """Determine whether an argument should be excluded from cache key calculation.

    Repositories and Sessions are excluded because they are infrastructure details
    that should not affect cache keys. Service instances (self) are NOT excluded
    to ensure different service instances have separate cache entries.

    Session detection uses curl_cffi-specific attributes (impersonate, cookies)
    rather than checking for repository attribute, which is too broad since
    Service instances also have a repository attribute.
    """
    if obj is None:
        return False
    cls_name = type(obj).__name__
    if cls_name.endswith(("Repository", "Session")):
        return True
    # Check for Session-specific attributes from curl_cffi
    return hasattr(obj, "impersonate") or hasattr(obj, "cookies")


def cached(ttl: float = 300.0, key_prefix: str = "") -> Callable[[_F], _F]:
    """Decorator to cache function results with a time-to-live.

    Args:
        ttl: Time-to-live in seconds.
        key_prefix: Optional prefix for the cache key.

    Returns:
        Decorated function.
    """

    def decorator(func: _F) -> _F:
        prefix = key_prefix or f"{func.__module__}.{func.__qualname__}"

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_args = [repr(a) for a in args if not _is_ignorable_arg(a)]
            cache_kwargs = {k: repr(v) for k, v in kwargs.items() if k != "session"}
            cache_key = f"{prefix}:{cache_args}:{sorted(cache_kwargs.items())}"

            cache = get_global_cache()
            cached_val = cache.get(cache_key)
            if cached_val is not None:
                return cached_val

            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl=ttl)
            return result

        return wrapper  # type: ignore[return-value]

    return decorator
