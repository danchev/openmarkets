"""
Unit tests for openmarkets.tools.extended_market module.

These tests cover bulk data download, ticker metadata, exchange info, market hours, ticker validation, currency data, and tool registration.
"""

import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import yfinance as yf

from openmarkets.tools.extended_market import (
    download_bulk_data,
    get_currency_data,
    get_exchange_info,
    get_market_hours,
    get_ticker_history_metadata,
    validate_tickers,
)
from openmarkets.tools.extended_market import (
    register as register_extended_market_tools,
)

###############################################################################
# Helpers
###############################################################################


def create_mock_df(data, index_dates=None):
    """
    Helper to create a pandas DataFrame with optional datetime index.
    """
    if index_dates:
        return pd.DataFrame(data, index=pd.to_datetime(index_dates))
    return pd.DataFrame(data)


###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def mock_yfinance_ticker():
    """
    Fixture to mock the yfinance.Ticker object with default info and empty history.
    """
    mock = MagicMock(spec=yf.Ticker)
    mock.info = {}
    mock.history = MagicMock(return_value=pd.DataFrame())
    return mock


###############################################################################
# Tests for download_bulk_data
###############################################################################
@pytest.mark.asyncio
@patch("yfinance.download")
async def test_download_bulk_data_success(mock_download):
    """
    Test download_bulk_data with valid data for multiple tickers.
    Should return correct structure and values.
    """
    tickers = ["AAPL", "MSFT"]
    mock_data = pd.DataFrame(
        {("AAPL", "Close"): [150, 151], ("MSFT", "Close"): [300, 301]},
        index=pd.to_datetime(["2023-01-01", "2023-01-02"]),
    )
    mock_download.return_value = mock_data

    result_str = await download_bulk_data(tickers, period="2d")
    result = json.loads(result_str)

    mock_download.assert_called_once()  # Basic check, can be more specific
    assert result["tickers"] == tickers
    assert "data" in result
    # New structure with orient='index' is {date_str: {col_str: val}}
    # Columns were ('AAPL', 'Close'), now "AAPL_Close"
    # Dates are index, e.g., "2023-01-01T00:00:00.000" (if .000 is added by to_json)
    # We can get the first date key from the result to check its content.
    first_date_key = list(result["data"].keys())[0]
    assert "AAPL_Close" in result["data"][first_date_key]
    assert "MSFT_Close" in result["data"][first_date_key]
    assert result["data"][first_date_key]["AAPL_Close"] == 150  # From mock_data


@pytest.mark.asyncio
@patch("yfinance.download")
async def test_download_bulk_data_empty(mock_download):
    """
    Test download_bulk_data when no data is returned.
    Should return an error message.
    """
    mock_download.return_value = pd.DataFrame()  # Empty data
    result_str = await download_bulk_data(["EMPTY"], period="1d")
    result = json.loads(result_str)
    assert "error" in result
    assert result["error"] == "No data available for the given tickers"


@pytest.mark.asyncio
@patch("yfinance.download")
async def test_download_bulk_data_exception(mock_download):
    """
    Test download_bulk_data when yfinance.download raises an exception.
    Should return an error message containing the exception.
    """
    mock_download.side_effect = Exception("Download failed")
    result_str = await download_bulk_data(["ERROR"], period="1d")
    result = json.loads(result_str)
    assert "error" in result
    assert "Failed to download bulk data: Download failed" in result["error"]


###############################################################################
# Tests for get_ticker_history_metadata
###############################################################################
@pytest.mark.asyncio
async def test_get_ticker_history_metadata_success(mock_yfinance_ticker):
    """
    Test get_ticker_history_metadata with valid history data.
    Should return correct symbol, dates, and columns.
    """
    hist_df = create_mock_df({"Close": [10, 11]}, index_dates=["2023-01-01", "2023-01-02"])
    mock_yfinance_ticker.history.return_value = hist_df

    with patch("yfinance.Ticker", return_value=mock_yfinance_ticker):
        result_str = await get_ticker_history_metadata("AAPL")
        result = json.loads(result_str)
        assert result["symbol"] == "AAPL"
        assert result["data_available"] is True
        assert result["latest_date"] == "2023-01-02T00:00:00"  # Pandas default str format for Timestamp
        assert result["earliest_available"] == "2023-01-01T00:00:00"
        assert "Close" in result["columns"]


@pytest.mark.asyncio
async def test_get_ticker_history_metadata_no_data(mock_yfinance_ticker):
    """
    Test get_ticker_history_metadata when no history data is available.
    Should indicate data is not available.
    """
    mock_yfinance_ticker.history.return_value = pd.DataFrame()  # Empty history
    with patch("yfinance.Ticker", return_value=mock_yfinance_ticker):
        result_str = await get_ticker_history_metadata("NODATA")
        result = json.loads(result_str)
        assert result["data_available"] is False


@pytest.mark.asyncio
async def test_get_ticker_history_metadata_history_exception(mock_yfinance_ticker):
    """
    Test get_ticker_history_metadata when history raises an exception.
    Should indicate data is not available.
    """
    mock_yfinance_ticker.history.side_effect = Exception("History fetch failed")
    with patch("yfinance.Ticker", return_value=mock_yfinance_ticker):
        result_str = await get_ticker_history_metadata("HISTFAIL")
        result = json.loads(result_str)
        assert result["data_available"] is False  # Should gracefully handle this


@pytest.mark.asyncio
async def test_get_ticker_history_metadata_ticker_exception(mock_yfinance_ticker):
    """
    Test get_ticker_history_metadata when Ticker creation raises an exception.
    Should return an error message containing the exception.
    """
    with patch("yfinance.Ticker", side_effect=Exception("Ticker creation failed")):
        result_str = await get_ticker_history_metadata("BADTICKER")
        result = json.loads(result_str)
        assert "error" in result
        assert "Failed to get metadata: Ticker creation failed" in result["error"]


###############################################################################
# Tests for get_exchange_info
###############################################################################
@pytest.mark.asyncio
async def test_get_exchange_info_success(mock_yfinance_ticker):
    """
    Test get_exchange_info with valid info data.
    Should return correct symbol, exchange, and currency.
    """
    mock_yfinance_ticker.info = {"exchange": "NMS", "fullExchangeName": "NASDAQ", "currency": "USD"}
    with patch("yfinance.Ticker", return_value=mock_yfinance_ticker):
        result_str = await get_exchange_info("AAPL")
        result = json.loads(result_str)
        assert result["symbol"] == "AAPL"
        assert result["exchange"] == "NMS"
        assert result["currency"] == "USD"


###############################################################################
# Tests for get_market_hours
###############################################################################
@pytest.mark.asyncio
async def test_get_market_hours_success(mock_yfinance_ticker):
    """
    Test get_market_hours with valid info data.
    Should return correct symbol, market state, and price.
    """
    mock_yfinance_ticker.info = {"exchange": "NMS", "marketState": "REGULAR", "regularMarketPrice": 150.0}
    with patch("yfinance.Ticker", return_value=mock_yfinance_ticker):
        result_str = await get_market_hours("AAPL")
        result = json.loads(result_str)
        assert result["symbol"] == "AAPL"
        assert result["marketState"] == "REGULAR"
        assert result["regularMarketPrice"] == 150.0


###############################################################################
# Tests for validate_tickers
###############################################################################
@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_validate_tickers_mixed(mock_ticker_constructor):
    """
    Test validate_tickers with a mix of valid, invalid, and error tickers.
    Should correctly classify and report each ticker.
    """

    def side_effect(symbol):
        mock_ticker = MagicMock()
        if symbol == "AAPL":
            mock_ticker.info = {"symbol": "AAPL", "shortName": "Apple Inc.", "exchange": "NMS", "quoteType": "EQUITY"}
            mock_ticker.history.return_value = create_mock_df({"Close": [10]}, index_dates=["2023-01-01"])
        elif symbol == "INVALIDTICKER":
            mock_ticker.info = {}  # Empty info
            mock_ticker.history.return_value = pd.DataFrame()  # Empty history
        elif symbol == "ERRORTICKER":
            # Simulate an error during info or history fetch for this specific ticker
            mock_ticker.history.side_effect = Exception("Fetch error")
            mock_ticker.info = {"symbol": "ERRORTICKER"}  # Info might partially exist
        return mock_ticker

    mock_ticker_constructor.side_effect = side_effect

    tickers = ["AAPL", "INVALIDTICKER", "ERRORTICKER"]
    result_str = await validate_tickers(tickers)
    result = json.loads(result_str)

    assert result["total_tickers"] == 3
    assert result["valid_count"] == 1
    assert result["invalid_count"] == 2

    results_map = {r["ticker"]: r for r in result["results"]}
    assert results_map["AAPL"]["valid"] is True
    assert results_map["AAPL"]["name"] == "Apple Inc."
    assert results_map["INVALIDTICKER"]["valid"] is False
    assert results_map["ERRORTICKER"]["valid"] is False
    assert "Failed to retrieve data" in results_map["ERRORTICKER"]["error"]


@pytest.mark.asyncio
async def test_validate_tickers_empty_list():
    """
    Test validate_tickers with an empty list.
    Should return zero counts and empty results.
    """
    result_str = await validate_tickers([])
    result = json.loads(result_str)
    assert result["total_tickers"] == 0
    assert result["valid_count"] == 0
    assert result["results"] == []


###############################################################################
# Tests for get_currency_data
###############################################################################
@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_currency_data_default_targets(mock_ticker_constructor):
    """
    Test get_currency_data with default target currencies.
    Should return correct rates and daily change percent for EUR.
    """

    def side_effect(symbol):
        mock_ticker = MagicMock()
        mock_ticker.info = {"shortName": symbol}
        if symbol == "USDEUR=X":
            mock_ticker.history.return_value = create_mock_df(
                {"Close": [0.9, 0.91]}, index_dates=["2023-01-01", "2023-01-02"]
            )
        elif symbol == "USDGBP=X":
            mock_ticker.history.return_value = create_mock_df(
                {"Close": [0.8, 0.81]}, index_dates=["2023-01-01", "2023-01-02"]
            )
        else:  # For other defaults like JPY, CAD etc.
            mock_ticker.history.return_value = create_mock_df(
                {"Close": [100, 101]}, index_dates=["2023-01-01", "2023-01-02"]
            )
        return mock_ticker

    mock_ticker_constructor.side_effect = side_effect

    result_str = await get_currency_data(base_currency="USD")
    result = json.loads(result_str)

    assert result["base_currency"] == "USD"
    assert result["count"] > 0
    eur_data = next(item for item in result["currency_rates"] if item["target"] == "EUR")
    assert eur_data["rate"] == 0.91
    assert eur_data["daily_change_percent"] == pytest.approx((0.91 - 0.9) / 0.9 * 100)


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_currency_data_custom_targets(mock_ticker_constructor):
    """
    Test get_currency_data with a custom target currency.
    Should return correct rate for JPY.
    """
    mock_ticker_instance = MagicMock()
    mock_ticker_instance.info = {"shortName": "USDJPY=X"}
    mock_ticker_instance.history.return_value = create_mock_df(
        {"Close": [130, 131]}, index_dates=["2023-01-01", "2023-01-02"]
    )
    mock_ticker_constructor.return_value = mock_ticker_instance  # Only one target

    result_str = await get_currency_data(base_currency="USD", target_currencies=["JPY"])
    result = json.loads(result_str)
    assert result["count"] == 1
    assert result["currency_rates"][0]["target"] == "JPY"
    assert result["currency_rates"][0]["rate"] == 131


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_currency_data_error_one_pair(mock_ticker_constructor):
    """
    Test get_currency_data when one currency pair fails.
    Should only return successful pairs.
    """

    def side_effect(symbol):
        mock_ticker = MagicMock()
        if symbol == "USDEUR=X":
            mock_ticker.info = {"shortName": "USDEUR=X"}
            mock_ticker.history.return_value = create_mock_df(
                {"Close": [0.9, 0.91]}, index_dates=["2023-01-01", "2023-01-02"]
            )
        elif symbol == "USDINVALID=X":
            mock_ticker.history.side_effect = Exception("Invalid pair")  # This pair will fail
        return mock_ticker

    mock_ticker_constructor.side_effect = side_effect

    result_str = await get_currency_data(base_currency="USD", target_currencies=["EUR", "INVALID"])
    result = json.loads(result_str)
    assert result["count"] == 1  # Only EUR should succeed
    assert result["currency_rates"][0]["target"] == "EUR"


###############################################################################
# Tests for register_extended_market_tools
###############################################################################


def test_register_extended_market_tools():
    """
    Test that register_extended_market_tools registers all expected public async functions as tools.
    """
    mock_mcp = MagicMock()
    mock_mcp.tool = MagicMock()

    register_extended_market_tools(mock_mcp)

    registered_funcs = [call_arg[0][0] for call_arg in mock_mcp.tool.return_value.call_args_list]

    expected_funcs = [
        download_bulk_data,
        get_ticker_history_metadata,
        get_exchange_info,
        get_market_hours,
        validate_tickers,
        get_currency_data,
    ]
    assert len(registered_funcs) == len(expected_funcs)
    for func in expected_funcs:
        assert func in registered_funcs, f"{func.__name__} not registered"
