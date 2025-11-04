"""
Unit tests for openmarkets.tools.market_data module.

These tests cover market status, sector performance, and index data endpoints.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

import openmarkets.tools.market_data as md

###############################################################################
# Tests for get_market_status
###############################################################################


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_market_status_success(mock_ticker_cls):
    """
    Test get_market_status with valid state data.
    Should return correct market state and related fields.
    """
    mock_market = MagicMock()
    mock_market.status = {
        "marketState": "OPEN",
        "exchangeTimezoneName": "America/New_York",
        "regularMarketTime": 1234567890,
        "preMarketPrice": 400.0,
        "postMarketPrice": 405.0,
        "currency": "USD",
    }
    with patch("yfinance.Market", return_value=mock_market):
        result = await md.get_market_status("US")
        data = json.loads(result)
        assert data["marketState"] == "OPEN"
        assert data["exchangeTimezoneName"] == "America/New_York"
        assert data["regularMarketTime"] == 1234567890
        assert data["preMarketPrice"] == 400.0
        assert data["postMarketPrice"] == 405.0
        assert data["currency"] == "USD"


###############################################################################
# Tests for get_sector_performance
###############################################################################


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_sector_performance_success(mock_ticker_cls):
    """
    Test get_sector_performance with valid info and history data.
    Should return a list of sector performance with correct current price.
    """

    def ticker_side_effect(etf):
        mock_ticker = MagicMock()
        mock_ticker.info = {"currentPrice": 100.0, "volume": 10000}
        import pandas as pd

        hist = pd.DataFrame({"Close": [90.0, 100.0], "Volume": [9000, 10000]})
        mock_ticker.history.return_value = hist
        return mock_ticker

    with patch("yfinance.Ticker", side_effect=ticker_side_effect):
        result = await md.get_sector_performance()
        data = json.loads(result)
        assert "sector_performance" in data
        assert isinstance(data["sector_performance"], list)
        assert data["sector_performance"][0]["current_price"] == 100.0


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_sector_performance_exception(mock_ticker_cls):
    """
    Test get_sector_performance when yfinance.Ticker raises an exception.
    Should return an error message in the result.
    """
    mock_ticker_cls.side_effect = Exception("fail")
    result = await md.get_sector_performance()
    data = json.loads(result)
    assert "error" in data


###############################################################################
# Tests for get_index_data
###############################################################################


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_index_data_success(mock_ticker_cls):
    """
    Test get_index_data with valid history data for an index.
    Should return correct symbol and current price.
    """

    def ticker_side_effect(index):
        mock_ticker = MagicMock()
        import pandas as pd

        hist = pd.DataFrame({"Close": [3900.0, 4000.0], "Volume": [100000, 110000]})
        mock_ticker.history.return_value = hist
        return mock_ticker

    with patch("yfinance.Ticker", side_effect=ticker_side_effect):
        result = await md.get_index_data(indices=["^GSPC"])
        data = json.loads(result)
        assert "indices" in data
        assert data["indices"][0]["symbol"] == "^GSPC"
        assert data["indices"][0]["current_price"] == 4000.0


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_index_data_exception(mock_ticker_cls):
    """
    Test get_index_data when yfinance.Ticker raises an exception.
    Should return an error message in the result.
    """
    mock_ticker_cls.side_effect = Exception("fail")
    result = await md.get_index_data(indices=["^GSPC"])
    data = json.loads(result)
    assert "error" in data
