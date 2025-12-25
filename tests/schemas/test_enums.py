"""
Tests for openmarkets.schemas.markets.MarketType enum.

This module tests the string comparison behavior of the MarketType enum.
"""

import unittest

from openmarkets.schemas.markets import MarketType


class TestMarketTypeEnum(unittest.TestCase):
    """Test string comparison for MarketType enum values."""

    def test_str_comparison(self):
        """Test that MarketType values compare equal to their string representations."""
        self.assertTrue(MarketType.US == "US")
        self.assertTrue(MarketType.ASIA == "ASIA")
        self.assertTrue(MarketType.EUROPE == "EUROPE")
        self.assertFalse(MarketType.GB == "US")


if __name__ == "__main__":
    unittest.main()
