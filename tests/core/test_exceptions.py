"""
Tests for openmarkets.core.exceptions

This module tests the custom exception hierarchy and behavior for OpenMarkets:
- APIError
- InvalidSymbolError
- OpenMarketsException
using pytest for assertion and error handling.
"""

import pytest

from openmarkets.core.exceptions import APIError, InvalidSymbolError, OpenMarketsException


@pytest.mark.parametrize(
    ("exc_type", "message"),
    [
        (APIError, "This is an API error"),
        (InvalidSymbolError, "This is an invalid symbol error"),
    ],
)
def test_custom_exceptions_can_be_raised(exc_type, message):
    with pytest.raises(exc_type):
        raise exc_type(message)


@pytest.mark.parametrize(
    ("exc_type", "message"),
    [
        (APIError, "API error instance"),
        (InvalidSymbolError, "Invalid symbol instance"),
    ],
)
def test_custom_exceptions_are_openmarkets_exception_subclasses(exc_type, message):
    try:
        raise exc_type(message)
    except OpenMarketsException:
        return
    except Exception:  # pragma: no cover
        pytest.fail(f"{exc_type.__name__} is not an instance of OpenMarketsException")


@pytest.mark.parametrize(
    "exc",
    [
        APIError("API error for isinstance check"),
        InvalidSymbolError("Invalid symbol for isinstance check"),
    ],
)
def test_custom_exception_instances_are_openmarkets_exception(exc):
    assert isinstance(exc, OpenMarketsException)
