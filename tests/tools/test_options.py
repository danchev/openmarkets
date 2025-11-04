"""
Unit tests for openmarkets.tools.options module.

These tests cover options expiration dates, option chain, volume analysis, moneyness, and volatility skew endpoints.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

import openmarkets.tools.options as opt

###############################################################################
# Tests for get_options_expiration_dates
###############################################################################


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_options_expiration_dates_success(mock_ticker_cls):
    """
    Test get_options_expiration_dates with valid options list.
    Should return the correct expiration dates.
    """
    mock_ticker = MagicMock()
    mock_ticker.options = ["2024-06-21", "2024-06-28"]
    mock_ticker_cls.return_value = mock_ticker

    result = await opt.get_options_expiration_dates("AAPL")
    data = json.loads(result)
    assert "expiration_dates" in data
    assert data["expiration_dates"] == ["2024-06-21", "2024-06-28"]


@pytest.mark.xfail
async def test_get_options_expiration_dates_error():
    """
    Test get_options_expiration_dates when yfinance.Ticker raises an exception.
    Should return an error message in the result.
    """
    with patch("yfinance.Ticker", side_effect=Exception("fail")):
        result = await opt.get_options_expiration_dates("AAPL")
        data = json.loads(result)
        assert "error" in data


###############################################################################
# Tests for get_option_chain
###############################################################################


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_option_chain_success(mock_ticker_cls):
    """
    Test get_option_chain with valid calls and puts data.
    Should return both calls and puts in the result.
    """
    mock_calls = MagicMock()
    mock_calls.to_dict.return_value = [{"strike": 100}]
    mock_puts = MagicMock()
    mock_puts.to_dict.return_value = [{"strike": 90}]
    mock_chain = MagicMock(calls=mock_calls, puts=mock_puts)
    mock_ticker = MagicMock()
    mock_ticker.options = ["2024-06-21"]
    mock_ticker.option_chain.return_value = mock_chain
    mock_ticker_cls.return_value = mock_ticker

    result = await opt.get_option_chain("AAPL", "2024-06-21")
    data = json.loads(result)
    assert "calls" in data and "puts" in data


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_option_chain_no_expirations(mock_ticker_cls):
    """
    Test get_option_chain when there are no expiration dates.
    Should return an error message in the result.
    """
    mock_ticker = MagicMock()
    mock_ticker.options = []
    mock_ticker_cls.return_value = mock_ticker

    result = await opt.get_option_chain("AAPL")
    data = json.loads(result)
    assert "error" in data


###############################################################################
# Tests for get_options_volume_analysis
###############################################################################


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_options_volume_analysis_success(mock_ticker_cls):
    """
    Test get_options_volume_analysis with valid calls and puts DataFrames.
    Should return correct total call and put volume.
    """
    import pandas as pd

    calls = pd.DataFrame({"volume": [10, 20], "openInterest": [100, 200]})
    puts = pd.DataFrame({"volume": [5, 15], "openInterest": [50, 150]})
    mock_chain = MagicMock(calls=calls, puts=puts)
    mock_ticker = MagicMock()
    mock_ticker.options = ["2024-06-21"]
    mock_ticker.option_chain.return_value = mock_chain
    mock_ticker_cls.return_value = mock_ticker

    result = await opt.get_options_volume_analysis("AAPL", "2024-06-21")
    data = json.loads(result)
    assert "total_call_volume" in data
    assert data["total_call_volume"] == 30
    assert data["total_put_volume"] == 20


###############################################################################
# Tests for get_options_by_moneyness
###############################################################################


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_options_by_moneyness_success(mock_ticker_cls):
    """
    Test get_options_by_moneyness with valid calls and puts DataFrames and current price.
    Should return filtered calls and puts within the moneyness range.
    """
    import pandas as pd

    calls = pd.DataFrame({"strike": [95, 100, 105]})
    puts = pd.DataFrame({"strike": [90, 100, 110]})
    mock_chain = MagicMock(calls=calls, puts=puts)
    mock_ticker = MagicMock()
    mock_ticker.options = ["2024-06-21"]
    mock_ticker.option_chain.return_value = mock_chain
    mock_ticker.info = {"currentPrice": 100}
    mock_ticker_cls.return_value = mock_ticker

    result = await opt.get_options_by_moneyness("AAPL", moneyness_range=0.05)
    data = json.loads(result)
    assert "calls" in data and "puts" in data
    assert all(95 <= c["strike"] <= 105 for c in data["calls"])
    assert all(95 <= p["strike"] <= 105 for p in data["puts"])


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_options_by_moneyness_no_price(mock_ticker_cls):
    """
    Test get_options_by_moneyness when current price is missing.
    Should return an error message in the result.
    """
    mock_chain = MagicMock(calls=[], puts=[])
    mock_ticker = MagicMock()
    mock_ticker.options = ["2024-06-21"]
    mock_ticker.option_chain.return_value = mock_chain
    mock_ticker.info = {}
    mock_ticker_cls.return_value = mock_ticker

    result = await opt.get_options_by_moneyness("AAPL")
    data = json.loads(result)
    assert "error" in data


###############################################################################
# Tests for get_options_skew
###############################################################################


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_options_skew_success_with_date(mock_ticker_cls):
    """
    Test get_options_skew with a specific expiration date and valid calls/puts DataFrames.
    Should return correct call_skew and put_skew.
    """
    import pandas as pd

    mock_ticker_instance = MagicMock()
    mock_ticker_cls.return_value = mock_ticker_instance

    # Mock options dates
    mock_ticker_instance.options = ("2025-01-01", "2025-02-01")

    # Mock option_chain data
    calls_data = {"strike": [100, 105], "impliedVolatility": [0.5, 0.45]}
    puts_data = {"strike": [90, 95], "impliedVolatility": [0.6, 0.55]}
    mock_calls_df = pd.DataFrame(calls_data)
    mock_puts_df = pd.DataFrame(puts_data)

    mock_option_chain_data = MagicMock()
    mock_option_chain_data.calls = mock_calls_df
    mock_option_chain_data.puts = mock_puts_df
    mock_ticker_instance.option_chain.return_value = mock_option_chain_data

    ticker = "TEST"
    expiration_date = "2025-01-01"
    result_str = await opt.get_options_skew(ticker, expiration_date)
    result_json = json.loads(result_str)

    assert "error" not in result_json
    assert "call_skew" in result_json
    assert "put_skew" in result_json
    assert result_json["call_skew"] == mock_calls_df[["strike", "impliedVolatility"]].to_dict("records")
    assert result_json["put_skew"] == mock_puts_df[["strike", "impliedVolatility"]].to_dict("records")
    mock_ticker_instance.option_chain.assert_called_once_with(expiration_date)


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_options_skew_success_no_date(mock_ticker_cls):
    """
    Test get_options_skew with no expiration date (should use nearest).
    Should return correct call_skew and put_skew.
    """
    import pandas as pd

    mock_ticker_instance = MagicMock()
    mock_ticker_cls.return_value = mock_ticker_instance

    # Mock options dates - nearest is '2025-01-01'
    nearest_expiration = "2025-01-01"
    mock_ticker_instance.options = (nearest_expiration, "2025-02-01")

    # Mock option_chain data
    calls_data = {"strike": [110, 115], "impliedVolatility": [0.3, 0.25]}
    puts_data = {"strike": [100, 105], "impliedVolatility": [0.4, 0.35]}
    mock_calls_df = pd.DataFrame(calls_data)
    mock_puts_df = pd.DataFrame(puts_data)

    mock_option_chain_data = MagicMock()
    mock_option_chain_data.calls = mock_calls_df
    mock_option_chain_data.puts = mock_puts_df
    mock_ticker_instance.option_chain.return_value = mock_option_chain_data

    ticker = "TEST"
    result_str = await opt.get_options_skew(ticker, None)  # No expiration_date
    result_json = json.loads(result_str)

    assert "error" not in result_json
    assert result_json["call_skew"] == mock_calls_df[["strike", "impliedVolatility"]].to_dict("records")
    assert result_json["put_skew"] == mock_puts_df[["strike", "impliedVolatility"]].to_dict("records")
    # Should be called with the first expiration date
    mock_ticker_instance.option_chain.assert_called_once_with(nearest_expiration)


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_options_skew_error_no_expirations(mock_ticker_cls):
    """
    Test get_options_skew when there are no expiration dates.
    Should return an error message in the result.
    """
    mock_ticker_instance = MagicMock()
    mock_ticker_cls.return_value = mock_ticker_instance
    mock_ticker_instance.options = ()  # No expiration dates

    ticker = "TEST"
    result_str = await opt.get_options_skew(ticker, None)
    result_json = json.loads(result_str)

    assert "error" in result_json
    assert result_json["error"] == "No options data available for this ticker."


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_options_skew_error_no_data_for_date(mock_ticker_cls):
    """
    Test get_options_skew when there is no data for the given expiration date.
    Should return an error message in the result.
    """
    import pandas as pd

    mock_ticker_instance = MagicMock()
    mock_ticker_cls.return_value = mock_ticker_instance

    expiration_date = "2025-01-01"
    mock_ticker_instance.options = (expiration_date,)

    # Mock option_chain to return empty calls and puts
    mock_empty_df = pd.DataFrame()
    mock_option_chain_empty = MagicMock()
    mock_option_chain_empty.calls = mock_empty_df
    mock_option_chain_empty.puts = mock_empty_df
    mock_ticker_instance.option_chain.return_value = mock_option_chain_empty

    ticker = "TEST"
    result_str = await opt.get_options_skew(ticker, expiration_date)
    result_json = json.loads(result_str)

    assert "error" in result_json
    assert result_json["error"] == f"No options data available for {ticker} on {expiration_date}."


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_options_skew_error_missing_strike_calls(mock_ticker_cls):
    """
    Test get_options_skew when 'strike' is missing in calls data.
    Should return an error message in the result.
    """
    import pandas as pd

    mock_ticker_instance = MagicMock()
    mock_ticker_cls.return_value = mock_ticker_instance

    expiration_date = "2025-01-01"
    mock_ticker_instance.options = (expiration_date,)

    # Calls data missing 'strike'
    calls_data = {"impliedVolatility": [0.5, 0.45]}
    puts_data = {"strike": [90, 95], "impliedVolatility": [0.6, 0.55]}
    mock_calls_df_missing_strike = pd.DataFrame(calls_data)
    mock_puts_df = pd.DataFrame(puts_data)

    mock_option_chain_data = MagicMock()
    mock_option_chain_data.calls = mock_calls_df_missing_strike
    mock_option_chain_data.puts = mock_puts_df  # Puts are fine
    mock_ticker_instance.option_chain.return_value = mock_option_chain_data

    ticker = "TEST"
    result_str = await opt.get_options_skew(ticker, expiration_date)
    result_json = json.loads(result_str)

    assert "error" in result_json
    assert result_json["error"] == "Missing 'strike' or 'impliedVolatility' in call options data."


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_options_skew_error_missing_iv_puts(mock_ticker_cls):
    """
    Test get_options_skew when 'impliedVolatility' is missing in puts data.
    Should return an error message in the result.
    """
    import pandas as pd

    mock_ticker_instance = MagicMock()
    mock_ticker_cls.return_value = mock_ticker_instance

    expiration_date = "2025-01-01"
    mock_ticker_instance.options = (expiration_date,)

    calls_data = {"strike": [100, 105], "impliedVolatility": [0.5, 0.45]}
    # Puts data missing 'impliedVolatility'
    puts_data = {"strike": [90, 95]}
    mock_calls_df = pd.DataFrame(calls_data)
    mock_puts_df_missing_iv = pd.DataFrame(puts_data)

    mock_option_chain_data = MagicMock()
    mock_option_chain_data.calls = mock_calls_df  # Calls are fine
    mock_option_chain_data.puts = mock_puts_df_missing_iv
    mock_ticker_instance.option_chain.return_value = mock_option_chain_data

    ticker = "TEST"
    result_str = await opt.get_options_skew(ticker, expiration_date)
    result_json = json.loads(result_str)

    assert "error" in result_json
    assert result_json["error"] == "Missing 'strike' or 'impliedVolatility' in put options data."


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_options_skew_error_yfinance_exception(mock_ticker_cls):
    """
    Test get_options_skew when yfinance raises an exception.
    Should return an error message in the result.
    """
    mock_ticker_instance = MagicMock()
    mock_ticker_cls.return_value = mock_ticker_instance

    expiration_date = "2025-01-01"
    mock_ticker_instance.options = (expiration_date,)

    # Mock option_chain to raise a generic exception
    error_message = "Test yfinance download error"
    mock_ticker_instance.option_chain.side_effect = Exception(error_message)

    ticker = "TEST"
    result_str = await opt.get_options_skew(ticker, expiration_date)
    result_json = json.loads(result_str)

    assert "error" in result_json
    assert result_json["error"] == f"Failed to get volatility skew analysis: {error_message}"


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_options_skew_empty_calls_data(mock_ticker_cls):
    """
    Test get_options_skew with empty calls DataFrame and valid puts DataFrame.
    Should return empty call_skew and valid put_skew.
    """
    import pandas as pd

    mock_ticker_instance = MagicMock()
    mock_ticker_cls.return_value = mock_ticker_instance

    expiration_date = "2025-01-01"
    mock_ticker_instance.options = (expiration_date,)

    # Empty calls DataFrame, valid puts DataFrame
    mock_empty_calls_df = pd.DataFrame(columns=["strike", "impliedVolatility"])
    puts_data = {"strike": [90, 95], "impliedVolatility": [0.6, 0.55]}
    mock_puts_df = pd.DataFrame(puts_data)

    mock_option_chain_data = MagicMock()
    mock_option_chain_data.calls = mock_empty_calls_df
    mock_option_chain_data.puts = mock_puts_df
    mock_ticker_instance.option_chain.return_value = mock_option_chain_data

    ticker = "TEST"
    result_str = await opt.get_options_skew(ticker, expiration_date)
    result_json = json.loads(result_str)

    assert "error" not in result_json
    assert "call_skew" in result_json
    assert result_json["call_skew"] == []  # Expect empty list for call_skew
    assert "put_skew" in result_json
    assert result_json["put_skew"] == mock_puts_df[["strike", "impliedVolatility"]].to_dict("records")


@pytest.mark.asyncio
@patch("yfinance.Ticker")
async def test_get_options_skew_empty_puts_data(mock_ticker_cls):
    """
    Test get_options_skew with valid calls DataFrame and empty puts DataFrame.
    Should return valid call_skew and empty put_skew.
    """
    import pandas as pd

    mock_ticker_instance = MagicMock()
    mock_ticker_cls.return_value = mock_ticker_instance

    expiration_date = "2025-01-01"
    mock_ticker_instance.options = (expiration_date,)

    # Valid calls DataFrame, empty puts DataFrame
    calls_data = {"strike": [100, 105], "impliedVolatility": [0.5, 0.45]}
    mock_calls_df = pd.DataFrame(calls_data)
    mock_empty_puts_df = pd.DataFrame(columns=["strike", "impliedVolatility"])

    mock_option_chain_data = MagicMock()
    mock_option_chain_data.calls = mock_calls_df
    mock_option_chain_data.puts = mock_empty_puts_df
    mock_ticker_instance.option_chain.return_value = mock_option_chain_data

    ticker = "TEST"
    result_str = await opt.get_options_skew(ticker, expiration_date)
    result_json = json.loads(result_str)

    assert "error" not in result_json
    assert "call_skew" in result_json
    assert result_json["call_skew"] == mock_calls_df[["strike", "impliedVolatility"]].to_dict("records")
    assert "put_skew" in result_json
    assert result_json["put_skew"] == []  # Expect empty list for put_skew
