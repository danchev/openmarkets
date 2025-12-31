"""
Tests for openmarkets.schemas.markets.MarketType enum.

This module tests the string comparison behavior of the MarketType enum.
"""

import pytest

from openmarkets.schemas.markets import MarketType


@pytest.mark.parametrize(
    ("market_type", "string_value", "should_match"),
    [
        (MarketType.US, "US", True),
        (MarketType.ASIA, "ASIA", True),
        (MarketType.EUROPE, "EUROPE", True),
        (MarketType.GB, "US", False),
    ],
)
def test_market_type_string_comparison(market_type, string_value, should_match):
    """Test that MarketType values compare correctly to their string representations."""
    if should_match:
        assert market_type == string_value
    else:
        assert market_type != string_value
