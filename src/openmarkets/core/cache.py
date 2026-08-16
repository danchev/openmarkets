"""In-memory thread-safe TTL cache for OpenMarkets.

Provides a lightweight time-to-live caching mechanism to protect upstream
Yahoo Finance endpoints against repetitive queries and rate-limiting.
"""

from __future__ import annotations

import copy
import functools
import threading
import time
import uuid
from typing import Any, Callable, ParamSpec, TypeVar, cast

_P = ParamSpec("_P")
_R = TypeVar("_R")


class TTLCache:
    """Thread-safe in-memory cache with time-to-live expiration."""

    def __init__(self, default_ttl: float = 300.0, maxsize: int = 1024) -> None:
        if default_ttl <= 0:
            raise ValueError("default_ttl must be greater than zero")
        if maxsize <= 0:
            raise ValueError("maxsize must be greater than zero")
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
            return copy.deepcopy(value)

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Store a value in the cache with a specified TTL."""
        ttl_seconds = ttl if ttl is not None else self._default_ttl
        if ttl_seconds <= 0:
            raise ValueError("ttl must be greater than zero")
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
            self._cache[key] = (copy.deepcopy(value), expires_at)

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()

    def __len__(self) -> int:
        with self._lock:
            now = time.monotonic()
            expired_keys = [key for key, (_, expires_at) in self._cache.items() if now > expires_at]
            for key in expired_keys:
                del self._cache[key]
            return len(self._cache)


_GLOBAL_CACHE = TTLCache(default_ttl=300.0)
# A cached function may legitimately call another cached function. A stripe
# collision in that nested path must not deadlock the calling thread.
_SINGLE_FLIGHT_LOCKS = tuple(threading.RLock() for _ in range(64))
_INSTANCE_ID_ATTR = "__openmarkets_cache_instance_id__"
_INSTANCE_ID_LOCK = threading.Lock()


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


def _cache_key_part(obj: Any) -> str:
    """Return a stable cache-key representation for one non-infrastructure arg.

    ``repr(object)`` commonly embeds a memory address. Addresses can be reused
    after an object is collected, which lets a new service instance inherit a
    stale result from the old instance. Service-like objects receive a UUID
    stored on the instance; immutable/value arguments continue to use repr.
    """
    if hasattr(obj, "__dict__"):
        token = getattr(obj, _INSTANCE_ID_ATTR, None)
        if token is None:
            with _INSTANCE_ID_LOCK:
                token = getattr(obj, _INSTANCE_ID_ATTR, None)
                if token is None:
                    token = uuid.uuid4().hex
                    try:
                        setattr(obj, _INSTANCE_ID_ATTR, token)
                    except (AttributeError, TypeError):
                        # A non-mutable object cannot carry a token; retain its
                        # normal repr as the least surprising fallback.
                        return repr(obj)
        return f"{type(obj).__module__}.{type(obj).__qualname__}#{token}"
    return repr(obj)


def cached(ttl: float = 300.0, key_prefix: str = "") -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """Decorator to cache function results with a time-to-live.

    Args:
        ttl: Time-to-live in seconds.
        key_prefix: Optional prefix for the cache key.

    Returns:
        Decorated function.
    """

    def decorator(func: Callable[_P, _R]) -> Callable[_P, _R]:
        module = getattr(func, "__module__", type(func).__module__)
        qualified_name = getattr(func, "__qualname__", type(func).__qualname__)
        prefix = key_prefix or f"{module}.{qualified_name}"

        @functools.wraps(func)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            cache_args = [_cache_key_part(a) for a in args if not _is_ignorable_arg(a)]
            cache_kwargs = {k: repr(v) for k, v in kwargs.items() if k != "session"}
            cache_key = f"{prefix}:{cache_args}:{sorted(cache_kwargs.items())}"

            cache = get_global_cache()
            cached_val = cache.get(cache_key)
            if cached_val is not None:
                return cached_val

            # A fixed lock stripe prevents same-key cache stampedes without
            # allowing a per-key lock dictionary to grow without bound.
            flight_lock = _SINGLE_FLIGHT_LOCKS[hash(cache_key) % len(_SINGLE_FLIGHT_LOCKS)]
            with flight_lock:
                cached_val = cache.get(cache_key)
                if cached_val is not None:
                    return cached_val
                result = func(*args, **kwargs)
                if result is not None:
                    cache.set(cache_key, result, ttl=ttl)
                return result

        return cast(Callable[_P, _R], wrapper)

    return decorator
