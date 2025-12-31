from __future__ import annotations

from datetime import datetime

import pytest


@pytest.fixture
def call_option_base_data() -> dict:
    """Base data for creating CallOption test instances."""
    return {
        "contractSymbol": "AAPL231215C00100000",
        "strike": 100,
        "lastPrice": 5.0,
        "bid": 4.9,
        "ask": 5.1,
        "change": 0.1,
        "percentChange": 0.02,
        "volume": 10,
        "openInterest": 100,
        "impliedVolatility": 0.2,
        "inTheMoney": True,
        "contractSize": "REGULAR",
        "currency": "USD",
    }


@pytest.fixture
def put_option_base_data() -> dict:
    """Base data for creating PutOption test instances."""
    return {
        "contractSymbol": "AAPL231215P00100000",
        "strike": 100,
        "lastPrice": 5.0,
        "bid": 4.9,
        "ask": 5.1,
        "change": 0.1,
        "percentChange": 0.02,
        "volume": 10,
        "openInterest": 100,
        "impliedVolatility": 0.2,
        "inTheMoney": False,
        "contractSize": "REGULAR",
        "currency": "USD",
    }


@pytest.fixture
def test_datetime() -> datetime:
    """Standard test datetime for schema tests."""
    return datetime(2025, 12, 18)


@pytest.fixture
def test_datetime_iso_string() -> str:
    """ISO-formatted datetime string for schema tests."""
    return "2025-12-18T00:00:00"
