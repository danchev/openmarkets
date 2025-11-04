"""
Unit tests for openmarkets.tools.calendar module.

These tests cover earnings calendar, earnings dates, market calendar info, and tool registration.
"""

import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from openmarkets.tools.calendar import (
    get_earnings_calendar,
    get_earnings_dates,
    get_market_calendar_info,
    register,
)

###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def mock_ticker():
    """
    Fixture to mock the yfinance.Ticker object.
    Sets up 'info' as a dict and 'calendar' as None by default.
    """
    mock = MagicMock()
    mock.info = {}
    mock.calendar = None
    return mock


###############################################################################
# Tests for get_earnings_calendar
###############################################################################


@pytest.mark.asyncio
async def test_get_earnings_calendar_success(mock_ticker):
    """
    Test get_earnings_calendar with valid data.
    XFAIL: This test is expected to fail if the mock does not match yfinance output.
    """
    data = {"Earnings Date": ["2024-08-15"], "EPS Estimate": [1.50]}
    df = pd.DataFrame(data)
    mock_ticker.calendar = df
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_earnings_calendar("AAPL")
        expected = df.to_dict(orient="records")
        actual = json.loads(result)
        assert actual == expected


@pytest.mark.asyncio
async def test_get_earnings_calendar_no_data(mock_ticker):
    """
    Test get_earnings_calendar with no data available.
    Should return an error message in JSON.
    """
    mock_ticker.calendar = None
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_earnings_calendar("AAPL")
        assert json.loads(result) == {"error": "No earnings calendar data available"}


###############################################################################
# Tests for get_earnings_dates
###############################################################################


@pytest.mark.asyncio
async def test_get_earnings_dates_success(mock_ticker):
    """
    Test get_earnings_dates with valid data.
    XFAIL: The mocked data structure may not match actual yfinance output.
    """
    earnings_data = {
        "earningsTimestamp": 1723716000,  # e.g., 2024-08-15T05:00:00 UTC
        "exDividendDate": 1721460000,  # e.g., 2024-07-20T02:20:00 UTC
        "dividendDate": 1722496800,  # e.g., 2024-08-01T02:20:00 UTC
    }
    mock_ticker.info = earnings_data
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_earnings_dates("AAPL")
        expected = {
            "earningsTimestamp": "2024-08-15T10:00:00+00:00",
            "exDividendDate": "2024-07-20T07:20:00+00:00",
            "dividendDate": "2024-08-01T07:20:00+00:00",
        }
        assert json.loads(result) == expected


###############################################################################
# Tests for get_market_calendar_info
###############################################################################


@pytest.mark.asyncio
async def test_get_market_calendar_info_success(mock_ticker):
    """
    Test get_market_calendar_info with valid data.
    Should return the expected market data as JSON.
    """
    market_data = {
        "exchange": "NASDAQ",
        "exchangeTimezoneName": "America/New_York",
        "exchangeTimezoneShortName": "EDT",
        "gmtOffSetMilliseconds": -14400000,
        "market": "us_market",
        "marketState": "REGULAR",
        "regularMarketTime": "2024-07-30T16:00:00Z",
        "regularMarketPreviousClose": 150.0,
        "preMarketPrice": 151.0,
        "preMarketTime": "2024-07-30T08:00:00Z",
        "postMarketPrice": 149.0,
        "postMarketTime": "2024-07-30T20:00:00Z",
    }
    mock_ticker.info = market_data
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_market_calendar_info("AAPL")
        expected_json = json.dumps(market_data, indent=2, default=str)
        assert json.loads(result) == json.loads(expected_json)


###############################################################################
# Tests for register_calendar_tools
###############################################################################


def test_register_calendar_tools():
    """
    Test that register_calendar_tools registers all expected public async functions as tools.
    """
    mock_mcp = MagicMock()
    mock_mcp.tool = MagicMock()

    register(mock_mcp)

    expected_calls = [
        get_earnings_calendar,
        get_earnings_dates,
        get_market_calendar_info,
    ]

    registered_funcs = [call_args[0][0] for call_args in mock_mcp.tool.return_value.call_args_list]

    assert len(registered_funcs) == len(expected_calls)
    for func in expected_calls:
        assert func in registered_funcs
