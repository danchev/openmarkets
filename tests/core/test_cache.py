import time

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
