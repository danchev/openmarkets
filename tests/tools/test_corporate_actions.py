"""
Unit tests for openmarkets.tools.corporate_actions module.

These tests cover dividends, splits, actions, dividend yield, and tool registration.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from openmarkets.tools.corporate_actions import (
    get_actions,
    get_dividend_yield,
    get_dividends_summary,
    get_splits_summary,
    register,
)

###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def mock_ticker():
    """
    Fixture to mock the yfinance.Ticker object.
    Sets up 'info', 'dividends', 'splits', 'actions', and a default empty history DataFrame.
    """
    mock = MagicMock()
    mock.info = {}
    mock.dividends = pd.Series(dtype="float64")
    mock.splits = pd.Series(dtype="float64")
    mock.actions = pd.DataFrame()
    empty_history_df = pd.DataFrame(
        {
            "Dividends": pd.Series(dtype="float64"),
            "Stock Splits": pd.Series(dtype="float64"),
        },
        index=pd.to_datetime([]),
    )
    mock.history = MagicMock(return_value=empty_history_df)
    return mock


###############################################################################
# Helpers
###############################################################################


def create_datetime_index(dates):
    """
    Helper to create a pandas.DatetimeIndex from a list of date strings or datetime objects.
    """
    return pd.DatetimeIndex([pd.to_datetime(date) for date in dates])


###############################################################################
# Tests for get_dividends_summary
###############################################################################


@pytest.mark.asyncio
async def test_get_dividends_success(mock_ticker):
    """
    Test get_dividends_summary with valid dividend data.
    Should return correct total and count.
    """
    dividends_dict = {
        pd.to_datetime("2023-01-01"): 0.1,
        pd.to_datetime("2023-04-01"): 0.1,
    }
    dividends_data_series = pd.Series(dividends_dict)
    mock_ticker.history.return_value = pd.DataFrame(
        {
            "Dividends": dividends_data_series,
            "Stock Splits": pd.Series(dtype="float64", index=dividends_data_series.index),
            "Close": pd.Series([1, 2], index=dividends_data_series.index),
        }
    )
    mock_ticker.dividends = dividends_data_series
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_dividends_summary("AAPL", period="1y")
        assert result["symbol"] == "AAPL"
        assert result["total_dividends"] == 0.2
        assert result["dividend_count"] == 2
        assert "dividends" in result


@pytest.mark.asyncio
async def test_get_dividends_with_date_range(mock_ticker):
    """
    Test get_dividends_summary with a specific date range.
    Should only include dividends within the range.
    """
    dividends_data = {
        pd.to_datetime("2023-01-15"): 0.1,
        pd.to_datetime("2023-02-15"): 0.12,
        pd.to_datetime("2023-03-15"): 0.1,
    }
    mock_ticker.dividends = pd.Series(dividends_data)
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_dividends_summary("MSFT", start_date="2023-01-01", end_date="2023-02-28")
        assert result["symbol"] == "MSFT"
        assert result["total_dividends"] == 0.22
        assert result["dividend_count"] == 2
        assert pd.to_datetime("2023-03-15") not in result["dividends"]


@pytest.mark.asyncio
async def test_get_dividends_no_data(mock_ticker):
    """
    Test get_dividends_summary when there is no dividend data.
    Should return zero totals and counts.
    """
    empty_series = pd.Series(dtype="float64")
    mock_ticker.history.return_value = pd.DataFrame(
        {
            "Dividends": empty_series,
            "Stock Splits": empty_series,
            "Close": pd.Series(dtype="float64"),
        },
        index=pd.to_datetime([]),
    )
    mock_ticker.dividends = empty_series
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_dividends_summary("NODIV")
        assert result["symbol"] == "NODIV"
        assert result["total_dividends"] == 0
        assert result["dividend_count"] == 0


@pytest.mark.asyncio
async def test_get_dividends_error(mock_ticker):
    """
    Test get_dividends_summary when yfinance raises an error.
    Should return an error message in the result.
    """
    mock_ticker.history.side_effect = Exception("Test yfinance error")
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_dividends_summary("ERROR")
        assert "error" in result
        assert result["error"] == "Test yfinance error"


###############################################################################
# Tests for get_splits_summary
###############################################################################


@pytest.mark.asyncio
async def test_get_splits_success(mock_ticker):
    splits_data = {pd.to_datetime("2023-01-01"): 2.0}
    mock_ticker.splits = pd.Series(splits_data)
    # Mock history to define the period start for filtering
    history_index_for_splits_success = create_datetime_index(["2022-01-01", "2023-06-01"])
    mock_ticker.history.return_value = pd.DataFrame(
        {
            "Close": [10, 11],  # Dummy data to make df.empty False
            "Dividends": pd.Series(dtype="float64", index=history_index_for_splits_success),
            "Stock Splits": pd.Series(dtype="float64", index=history_index_for_splits_success),
        },
        index=history_index_for_splits_success,
    )

    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_splits_summary("AAPL", period="1y")  # period will make it look back from history end
        assert result["symbol"] == "AAPL"
        assert result["split_count"] == 1
        assert "splits" in result


@pytest.mark.asyncio
async def test_get_splits_no_data(mock_ticker):
    mock_ticker.splits = pd.Series(dtype="float64")  # No splits data
    history_index_no_splits = create_datetime_index(["2022-01-01"])
    mock_ticker.history.return_value = pd.DataFrame(
        {
            "Close": [10],  # Dummy data
            "Dividends": pd.Series(dtype="float64", index=history_index_no_splits),
            "Stock Splits": pd.Series(dtype="float64", index=history_index_no_splits),
        },
        index=history_index_no_splits,
    )
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_splits_summary("NOSPLIT")
        assert result["symbol"] == "NOSPLIT"
        assert result["split_count"] == 0


@pytest.mark.asyncio
async def test_get_splits_period_filtering(mock_ticker):
    splits_data = {
        pd.to_datetime("2020-03-01"): 2.0,  # Outside 1y period if history ends 2023
        pd.to_datetime("2023-05-01"): 3.0,  # Inside 1y period
    }
    mock_ticker.splits = pd.Series(splits_data)
    # Let history start from 2022-06-01 for a 1y period, so 2020 split is filtered out
    history_index_filter = create_datetime_index(["2022-06-01", "2023-06-01"])
    mock_ticker.history.return_value = pd.DataFrame(
        {
            "Close": [10, 11],  # Dummy data
            "Dividends": pd.Series(dtype="float64", index=history_index_filter),
            "Stock Splits": pd.Series(dtype="float64", index=history_index_filter),
        },
        index=history_index_filter,
    )

    with patch("yfinance.Ticker", return_value=mock_ticker):
        # Simplified prints for focusing on history.empty
        print(
            f"DEBUG_TEST: mock_ticker.history.return_value.empty BEFORE call = {mock_ticker.history.return_value.empty}"
        )
        # The following line is just for sanity checking the mock in the test's context
        # history_in_test_context = mock_ticker.history(period="1y")
        # print(f"DEBUG_TEST: history_in_test_context.empty = {history_in_test_context.empty}")

        result = await get_splits_summary("AAPL", period="1y")
        print(f"DEBUG_TEST: result = {result}")
        assert result["split_count"] == 1
        assert pd.to_datetime("2023-05-01") in result["splits"]  # Keys are Timestamps


###############################################################################
# Tests for get_actions
###############################################################################


@pytest.mark.asyncio
async def test_get_actions_success(mock_ticker):
    actions_data = pd.DataFrame(
        {"Dividends": [0.1, 0, 0.12], "Stock Splits": [0, 2.0, 0]},
        index=create_datetime_index(["2023-01-01", "2023-02-01", "2023-03-01"]),
    )
    mock_ticker.actions = actions_data
    history_index_actions = create_datetime_index(["2022-01-01", "2023-06-01"])
    mock_ticker.history.return_value = pd.DataFrame(
        {
            "Close": [10, 11],  # Dummy
            "Dividends": pd.Series(dtype="float64", index=history_index_actions),  # Needed by yf
            "Stock Splits": pd.Series(dtype="float64", index=history_index_actions),  # Needed by yf
        },
        index=history_index_actions,
    )

    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_actions("AAPL", period="1y")
        assert result["symbol"] == "AAPL"
        assert result["total_actions"] == 3  # All actions from the mock
        assert "actions" in result


@pytest.mark.asyncio
async def test_get_actions_no_data(mock_ticker):
    mock_ticker.actions = pd.DataFrame()  # No actions data
    history_index_no_actions = create_datetime_index(["2022-01-01"])
    mock_ticker.history.return_value = pd.DataFrame(
        {
            "Close": [10],  # Dummy
            "Dividends": pd.Series(dtype="float64", index=history_index_no_actions),
            "Stock Splits": pd.Series(dtype="float64", index=history_index_no_actions),
        },
        index=history_index_no_actions,
    )
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_actions("NOACTION")
        assert result["symbol"] == "NOACTION"
        assert result["total_actions"] == 0


###############################################################################
# Tests for get_dividend_yield
###############################################################################


@pytest.mark.asyncio
async def test_get_dividend_yield_success(mock_ticker):
    # TTM dividends require careful date mocking
    now = datetime.now()
    dividends_index = create_datetime_index(
        [
            now - timedelta(days=400),  # older than 1 year
            now - timedelta(days=300),  # 0.1
            now - timedelta(days=200),  # 0.1
            now - timedelta(days=100),  # 0.1
            now - timedelta(days=10),  # 0.12 -> TTM = 0.42
        ]
    )
    dividends_values = [0.08, 0.1, 0.1, 0.1, 0.12]
    mock_ticker.dividends = pd.Series(dividends_values, index=dividends_index)

    mock_ticker.info = {
        "currentPrice": 20.0,
        "dividendRate": 0.48,  # Forward rate
        "dividendYield": 0.024,  # Forward yield
        "payoutRatio": 0.5,
        "exDividendDate": (now - timedelta(days=5)).timestamp(),  # Needs to be timestamp
        "dividendDate": (now + timedelta(days=5)).timestamp(),
    }

    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_dividend_yield("AAPL")
        assert result["symbol"] == "AAPL"
        assert result["current_price"] == 20.0
        assert result["ttm_dividends"] == pytest.approx(0.42)  # 0.1 * 3 + 0.12
        assert result["dividend_yield_percent"] == pytest.approx((0.42 / 20.0) * 100)
        assert result["forward_dividend_rate"] == 0.48


@pytest.mark.asyncio
async def test_get_dividend_yield_no_dividends(mock_ticker):
    mock_ticker.dividends = pd.Series(dtype="float64")  # No dividends
    mock_ticker.info = {"currentPrice": 100.0}
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_dividend_yield("NODIVYIELD")
        assert result["ttm_dividends"] == 0
        assert result["dividend_yield_percent"] == 0


@pytest.mark.asyncio
async def test_get_dividend_yield_zero_price(mock_ticker):
    dividends_index = create_datetime_index([datetime.now() - timedelta(days=100)])
    mock_ticker.dividends = pd.Series([0.1], index=dividends_index)
    mock_ticker.info = {"currentPrice": 0.0}  # Zero price
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_dividend_yield("ZEROPRICE")
        assert result["ttm_dividends"] == 0.1
        assert result["dividend_yield_percent"] == 0  # Cannot divide by zero


###############################################################################
# Tests for register_corporate_actions_tools
###############################################################################


def test_register_corporate_actions_tools():
    """
    Test that register_corporate_actions_tools registers all expected public async functions as tools.
    """
    mock_mcp = MagicMock()
    mock_mcp.tool = MagicMock()

    register(mock_mcp)

    expected_calls = [
        get_dividends_summary,
        get_splits_summary,
        get_actions,
        get_dividend_yield,
    ]

    registered_funcs = [call_arg[0][0] for call_arg in mock_mcp.tool.return_value.call_args_list]

    assert len(registered_funcs) == len(expected_calls)
    for func in expected_calls:
        assert func in registered_funcs
