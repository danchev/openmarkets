"""
Tests for openmarkets.tools.stock_info

This module contains async tests for the stock_info tool functions, covering:
- Multiple tickers data retrieval
- Stock info details
- Company officers
- Institutional, major, and mutual fund holders
using pytest, unittest.mock, and yfinance mocks.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

import openmarkets.tools.stock_info as stock_info

# =========================
# Multiple Tickers Section
# =========================


@pytest.mark.asyncio
@patch("yfinance.download")
async def test_get_multiple_tickers_no_data(mock_download):
    """Test get_multiple_tickers returns error for None or empty DataFrame."""
    mock_download.return_value = None  # Simulate yf.download returning None
    result_str = await stock_info.get_multiple_tickers(["EMPTYTICKER"])
    result = json.loads(result_str)
    assert "error" in result
    assert result["error"] == "No data available for the given tickers"

    import pandas as pd

    # Simulate yf.download returning an empty DataFrame
    mock_download.return_value = pd.DataFrame()
    result_str_empty_df = await stock_info.get_multiple_tickers(["EMPTYTICKERDF"])
    result_empty_df = json.loads(result_str_empty_df)
    assert "error" in result_empty_df
    assert result_empty_df["error"] == "No data available for the given tickers"


# =========================
# Stock Info Section
# =========================


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_stock_info(mock_ticker_cls):
    """Test get_stock_info returns correct info for a valid ticker."""
    mock_info = {
        "symbol": "AAPL",
        "shortName": "Apple Inc.",
        "longName": "Apple Incorporated",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "marketCap": 1000000000,
        "currentPrice": 150.0,
        "previousClose": 148.0,
        "open": 149.0,
        "dayLow": 147.5,
        "dayHigh": 151.0,
        "volume": 1000000,
        "averageVolume": 900000,
        "beta": 1.2,
        "trailingPE": 25.0,
        "forwardPE": 23.0,
        "dividendYield": 0.005,
        "payoutRatio": 0.2,
        "fiftyTwoWeekLow": 120.0,
        "fiftyTwoWeekHigh": 180.0,
        "priceToBook": 30.0,
        "debtToEquity": 1.5,
        "returnOnEquity": 0.3,
        "returnOnAssets": 0.15,
        "freeCashflow": 500000000,
        "operatingCashflow": 600000000,
        "website": "https://apple.com",
        "country": "United States",
        "city": "Cupertino",
        "phone": "123-456-7890",
        "fullTimeEmployees": 100000,
        "longBusinessSummary": "Apple designs, manufactures, and markets smartphones.",
    }
    mock_ticker = MagicMock()
    mock_ticker.info = mock_info
    mock_ticker_cls.return_value = mock_ticker

    result = await stock_info.get_stock_info("AAPL")
    data = json.loads(result)
    assert data["symbol"] == "AAPL"
    assert data["shortName"] == "Apple Inc."
    assert data["currentPrice"] == 150.0


@pytest.mark.asyncio
@patch("yfinance.download")
async def test_get_multiple_tickers(mock_download):
    """Test get_multiple_tickers returns data for multiple tickers."""
    import pandas as pd

    df = pd.DataFrame(
        {
            ("AAPL", "Close"): [150.0],
            ("GOOGL", "Close"): [2800.0],
        },
        index=[pd.Timestamp("2023-01-01")],
    )
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    mock_download.return_value = df

    result = await stock_info.get_multiple_tickers(["AAPL", "GOOGL"])
    data = json.loads(result)
    assert "AAPL" in str(data)
    assert "GOOGL" in str(data)


# =========================
# Company Officers Section
# =========================


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_company_officers(mock_ticker_cls):
    """Test get_company_officers returns officers list for a valid ticker."""
    officers = [{"name": "Tim Cook", "title": "CEO"}]
    mock_ticker = MagicMock()
    mock_ticker.get_info.return_value = {"companyOfficers": officers}
    mock_ticker_cls.return_value = mock_ticker

    result = await stock_info.get_company_officers("AAPL")
    data = json.loads(result)
    assert isinstance(data, list)
    assert data[0]["name"] == "Tim Cook"


# =========================
# Institutional Holders Section
# =========================


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_institutional_holders(mock_ticker_cls):
    """Test get_institutional_holders returns holders DataFrame as JSON."""
    import pandas as pd

    df = pd.DataFrame({"Holder": ["Vanguard"], "Shares": [1000000]})
    mock_ticker = MagicMock()
    mock_ticker.institutional_holders = df
    mock_ticker_cls.return_value = mock_ticker

    result = await stock_info.get_institutional_holders("AAPL")
    json.loads(result)
    assert "Vanguard" in result


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_institutional_holders_none(mock_ticker_cls):
    """Test get_institutional_holders returns error if no holders."""
    mock_ticker = MagicMock()
    mock_ticker.institutional_holders = None
    mock_ticker_cls.return_value = mock_ticker

    result = await stock_info.get_institutional_holders("AAPL")
    data = json.loads(result)
    assert "error" in data


# =========================
# Major Holders Section
# =========================


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_major_holders(mock_ticker_cls):
    """Test get_major_holders returns major holders DataFrame as JSON."""
    import pandas as pd

    df = pd.DataFrame({0: ["60% held by institutions"]})
    mock_ticker = MagicMock()
    mock_ticker.major_holders = df
    mock_ticker_cls.return_value = mock_ticker

    result = await stock_info.get_major_holders("AAPL")
    assert "institutions" in result


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_major_holders_none(mock_ticker_cls):
    """Test get_major_holders returns error if no holders."""
    mock_ticker = MagicMock()
    mock_ticker.major_holders = None
    mock_ticker_cls.return_value = mock_ticker

    result = await stock_info.get_major_holders("AAPL")
    data = json.loads(result)
    assert "error" in data


# =========================
# Mutual Fund Holders Section
# =========================


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_mutualfund_holders(mock_ticker_cls):
    """Test get_mutualfund_holders returns mutual fund holders DataFrame as JSON."""
    import pandas as pd

    df = pd.DataFrame({"Holder": ["Fidelity"], "Shares": [500000]})
    mock_ticker = MagicMock()
    mock_ticker.mutualfund_holders = df
    mock_ticker_cls.return_value = mock_ticker

    result = await stock_info.get_mutualfund_holders("AAPL")
    assert "Fidelity" in result


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_mutualfund_holders_none(mock_ticker_cls):
    """Test get_mutualfund_holders returns error if no holders."""
    mock_ticker = MagicMock()
    mock_ticker.mutualfund_holders = None
    mock_ticker_cls.return_value = mock_ticker

    result = await stock_info.get_mutualfund_holders("AAPL")
    data = json.loads(result)
    assert "error" in data
