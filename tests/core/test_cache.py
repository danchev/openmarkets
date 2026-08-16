import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from openmarkets.core.cache import TTLCache, cached, get_global_cache


def test_ttl_cache_basic():
    cache = TTLCache(default_ttl=1.0, maxsize=3)
    cache.set("key1", "val1")
    assert cache.get("key1") == "val1"
    assert cache.get("missing") is None
    assert len(cache) == 1

    cache.clear()
    assert len(cache) == 0
    assert cache.get("key1") is None


def test_ttl_cache_expiration():
    cache = TTLCache(default_ttl=0.1)
    cache.set("temp", "data")
    assert cache.get("temp") == "data"
    time.sleep(0.15)
    assert cache.get("temp") is None


def test_ttl_cache_maxsize_eviction():
    cache = TTLCache(default_ttl=10.0, maxsize=2)
    cache.set("k1", "v1")
    cache.set("k2", "v2")
    cache.set("k3", "v3")  # should evict oldest/expired
    assert cache.get("k3") == "v3"
    assert len(cache) <= 2


def test_cached_decorator():
    call_count = 0

    @cached(ttl=1.0, key_prefix="test_fn")
    def compute(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    assert compute(5) == 10
    assert call_count == 1
    # Cached call
    assert compute(5) == 10
    assert call_count == 1
    # Different arg
    assert compute(6) == 12
    assert call_count == 2


def test_get_global_cache():
    cache = get_global_cache()
    assert isinstance(cache, TTLCache)


def test_cache_validates_capacity_and_ttl():
    with pytest.raises(ValueError, match="maxsize"):
        TTLCache(maxsize=0)
    cache = TTLCache()
    with pytest.raises(ValueError, match="ttl"):
        cache.set("x", 1, ttl=0)


def test_cache_does_not_share_mutable_values():
    cache = TTLCache()
    original = {"items": [1]}
    cache.set("x", original)
    original["items"].append(2)
    fetched = cache.get("x")
    fetched["items"].append(3)
    assert cache.get("x") == {"items": [1]}


def test_cached_decorator_coalesces_same_key_concurrent_misses():
    calls = 0

    @cached(ttl=10, key_prefix="single-flight-regression")
    def slow(value: int) -> int:
        nonlocal calls
        calls += 1
        time.sleep(0.05)
        return value

    with ThreadPoolExecutor(max_workers=8) as executor:
        assert list(executor.map(slow, [7] * 8)) == [7] * 8
    assert calls == 1


def test_nested_cached_calls_do_not_deadlock_on_lock_stripe_collision(monkeypatch):
    """Nested cached functions can hash to the same fixed lock stripe."""
    import openmarkets.core.cache as cache_module

    get_global_cache().clear()
    lock_type = type(cache_module._SINGLE_FLIGHT_LOCKS[0])
    monkeypatch.setattr(cache_module, "_SINGLE_FLIGHT_LOCKS", (lock_type(),))

    @cached(ttl=10, key_prefix="nested-cache-inner")
    def inner(value: int) -> int:
        return value * 2

    @cached(ttl=10, key_prefix="nested-cache-outer")
    def outer(value: int) -> int:
        return inner(value) + 1

    result: list[int] = []
    worker = threading.Thread(target=lambda: result.append(outer(4)), daemon=True)
    worker.start()
    worker.join(timeout=1)

    assert not worker.is_alive(), "same-stripe nested cache call deadlocked"
    assert result == [9]
