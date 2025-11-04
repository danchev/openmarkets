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

# =========================
# APIError Section
# =========================


def test_raise_api_error():
    """Test that APIError can be raised and caught."""
    with pytest.raises(APIError):
        raise APIError("This is an API error")


# =========================
# InvalidSymbolError Section
# =========================


def test_raise_invalid_symbol_error():
    """Test that InvalidSymbolError can be raised and caught."""
    with pytest.raises(InvalidSymbolError):
        raise InvalidSymbolError("This is an invalid symbol error")


# =========================
# OpenMarketsException Hierarchy Section
# =========================


def test_exceptions_are_openmarkets_exception():
    """Test that APIError and InvalidSymbolError are instances of OpenMarketsException."""
    try:
        raise APIError("API error instance")
    except OpenMarketsException:
        pass  # Expected
    except Exception:
        pytest.fail("APIError is not an instance of OpenMarketsException")

    try:
        raise InvalidSymbolError("Invalid symbol instance")
    except OpenMarketsException:
        pass  # Expected
    except Exception:
        pytest.fail("InvalidSymbolError is not an instance of OpenMarketsException")


def test_api_error_is_instance_of_openmarkets_exception():
    """Test isinstance for APIError and OpenMarketsException."""
    api_err = APIError("API error for isinstance check")
    assert isinstance(api_err, OpenMarketsException)


def test_invalid_symbol_error_is_instance_of_openmarkets_exception():
    """Test isinstance for InvalidSymbolError and OpenMarketsException."""
    invalid_symbol_err = InvalidSymbolError("Invalid symbol for isinstance check")
    assert isinstance(invalid_symbol_err, OpenMarketsException)
