"""Tests to verify the cache key bug fix.

This test file validates that different service instances maintain
separate cache entries instead of sharing them.
"""

from typing import Any, cast
from unittest.mock import MagicMock

from openmarkets.core.cache import get_global_cache
from openmarkets.services.stock import StockService


def test_different_service_instances_have_separate_cache_entries():
    """Verify that different StockService instances don't share cache.

    This validates the fix for the bug where _is_ignorable_arg() was
    filtering out 'self', causing different service instances to share
    the same cache entry.
    """
    # Clear global cache
    get_global_cache().clear()

    # Create mock repository that tracks calls
    mock_repo = MagicMock()
    mock_repo.get_fast_info.return_value = {"symbol": "AAPL", "price": 100.0}

    # Create two different service instances with different sessions
    session_A = MagicMock()
    session_B = MagicMock()

    s1 = StockService(repository=mock_repo, session=session_A)
    s2 = StockService(repository=mock_repo, session=session_B)

    # s1 calls get_fast_info("AAPL")
    result1 = s1.get_fast_info("AAPL")
    assert result1 == {"symbol": "AAPL", "price": 100.0}
    assert mock_repo.get_fast_info.call_count == 1

    # s2 calls get_fast_info("AAPL")
    # Should NOT hit cache because it's a different service instance
    result2 = s2.get_fast_info("AAPL")
    assert result2 == {"symbol": "AAPL", "price": 100.0}

    # Repository should be called twice (not reused from cache)
    assert mock_repo.get_fast_info.call_count == 2

    # Verify both results are identical
    assert result1 == result2

    # Clean up
    get_global_cache().clear()


def test_same_service_instance_uses_cache():
    """Verify that the same service instance still uses cache properly."""
    # Clear global cache
    get_global_cache().clear()

    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.get_fast_info.return_value = {"symbol": "AAPL", "price": 100.0}

    # Create a single service instance
    service = StockService(repository=mock_repo)

    # Call get_fast_info twice for the same ticker
    result1 = service.get_fast_info("AAPL")
    result2 = service.get_fast_info("AAPL")

    # Repository should be called only once (cached on second call)
    assert mock_repo.get_fast_info.call_count == 1

    # Results should be identical
    assert result1 == result2

    # Clean up
    get_global_cache().clear()


def test_cache_identity_does_not_depend_on_reused_object_address():
    """A new service instance cannot inherit a collected instance's result."""
    get_global_cache().clear()

    first_repo = MagicMock()
    first_repo.get_fast_info.return_value = {"symbol": "AAPL", "price": 100.0}
    first = StockService(repository=first_repo)
    first_result = cast(dict[str, Any], first.get_fast_info("AAPL"))
    assert first_result["price"] == 100.0

    second_repo = MagicMock()
    second_repo.get_fast_info.return_value = {"symbol": "AAPL", "price": 200.0}
    second = StockService(repository=second_repo)
    second_result = cast(dict[str, Any], second.get_fast_info("AAPL"))
    assert second_result["price"] == 200.0
    assert second_repo.get_fast_info.call_count == 1

    get_global_cache().clear()


def test_cache_distinguishes_different_tickers():
    """Verify cache correctly distinguishes between different tickers."""
    # Clear global cache
    get_global_cache().clear()

    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.get_fast_info.side_effect = [
        {"symbol": "AAPL", "price": 100.0},
        {"symbol": "MSFT", "price": 200.0},
    ]

    # Create a single service instance
    service = StockService(repository=mock_repo)

    # Call for different tickers
    result1 = cast(dict[str, Any], service.get_fast_info("AAPL"))
    result2 = cast(dict[str, Any], service.get_fast_info("MSFT"))
    result1_cached = cast(dict[str, Any], service.get_fast_info("AAPL"))

    # Repository should be called twice (not three times)
    assert mock_repo.get_fast_info.call_count == 2

    # Verify results
    assert result1["symbol"] == "AAPL"
    assert result2["symbol"] == "MSFT"
    assert result1_cached["symbol"] == "AAPL"
    assert result1 == result1_cached

    # Clean up
    get_global_cache().clear()
