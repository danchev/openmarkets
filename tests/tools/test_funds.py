"""
Unit tests for openmarkets.tools.funds plugin functions.

These tests cover fund profile, holdings, sector allocation, performance, comparison, and tool registration logic.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from openmarkets.tools import funds


@pytest.mark.asyncio
class TestGetFundProfile:
    """Tests for get_fund_profile."""

    async def test_success(self):
        mock_info = {
            "symbol": "VFIAX",
            "longName": "Vanguard 500 Index Fund Admiral Shares",
            "fundFamily": "Vanguard",
            "category": "Large Blend",
            # "fundInceptionDate": "2000-11-13",
            "totalAssets": 1.0e12,
            "annualReportExpenseRatio": 0.0004,
            "beta3Year": 1.0,
            "yield": 0.015,
            "ytdReturn": 0.1,
            "threeYearAverageReturn": 0.12,
            "fiveYearAverageReturn": 0.11,
            "morningStarRiskRating": 2,
            "morningStarOverallRating": 5,
            "currency": "USD",
            "navPrice": 300.0,
        }
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result_str = await funds.get_fund_profile("VFIAX")
            mock_yf_ticker.assert_called_once_with("VFIAX")
            result_json = json.loads(result_str)
            assert result_json["longName"] == mock_info["longName"]
            assert result_json["netExpenseRatio"] == mock_info["annualReportExpenseRatio"]  # Key name mapping

    async def test_missing_keys(self):
        mock_info = {"symbol": "VFIAX", "longName": "Vanguard 500 Index Fund Admiral Shares"}  # Many keys missing
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info

        with patch("yfinance.Ticker", return_value=mock_ticker_instance):
            result_str = await funds.get_fund_profile("VFIAX")
            result_json = json.loads(result_str)
            assert result_json["longName"] == mock_info["longName"]
            assert result_json["fundFamily"] is None
            assert result_json["totalAssets"] is None
            assert result_json["netExpenseRatio"] is None

    async def test_yfinance_exception(self):
        with patch("yfinance.Ticker", side_effect=Exception("Test yf error")):
            result_str = await funds.get_fund_profile("ERROR_TICKER")
            result_json = json.loads(result_str)
            assert "error" in result_json
            assert "Failed to get fund profile: Test yf error" in result_json["error"]


@pytest.mark.asyncio
class TestGetFundHoldings:
    """Tests for get_fund_holdings."""

    async def test_success_with_holdings(self):
        mock_holdings_data = [{"symbol": "AAPL", "weight": 0.1}, {"symbol": "MSFT", "weight": 0.08}]
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {"holdings": mock_holdings_data}

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            # Test default count (20)
            result_str = await funds.get_fund_holdings("VTSAX")
            mock_yf_ticker.assert_called_once_with("VTSAX")
            result_json = json.loads(result_str)
            assert result_json["symbol"] == "VTSAX"
            assert len(result_json["top_holdings"]) == 2
            assert result_json["top_holdings"] == mock_holdings_data

            # Test count smaller than available
            mock_yf_ticker.reset_mock()
            result_str_count1 = await funds.get_fund_holdings("VTSAX", count=1)
            result_json_count1 = json.loads(result_str_count1)
            assert len(result_json_count1["top_holdings"]) == 1
            assert result_json_count1["top_holdings"] == [mock_holdings_data[0]]

            # Test count larger than available
            mock_yf_ticker.reset_mock()
            result_str_count_large = await funds.get_fund_holdings("VTSAX", count=10)
            result_json_count_large = json.loads(result_str_count_large)
            assert len(result_json_count_large["top_holdings"]) == 2  # Should return all available
            assert result_json_count_large["top_holdings"] == mock_holdings_data

    async def test_no_holdings_data_key_missing(self):
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {}  # 'holdings' key is missing

        with patch("yfinance.Ticker", return_value=mock_ticker_instance):
            result_str = await funds.get_fund_holdings("NOHOLD")
            result_json = json.loads(result_str)
            assert result_json == {"error": "No holdings data available for this fund"}

    async def test_empty_holdings_list(self):
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {"holdings": []}  # holdings list is empty

        with patch("yfinance.Ticker", return_value=mock_ticker_instance):
            result_str = await funds.get_fund_holdings("EMPTYHOLD")
            result_json = json.loads(result_str)
            assert result_json == {"error": "No holdings data available for this fund"}

    async def test_yfinance_exception(self):
        with patch("yfinance.Ticker", side_effect=Exception("YF Holdings Error")):
            result_str = await funds.get_fund_holdings("ERROR_TICKER")
            result_json = json.loads(result_str)
            assert "error" in result_json
            assert "Failed to get fund holdings: YF Holdings Error" in result_json["error"]


@pytest.mark.asyncio
class TestGetFundSectorAllocation:
    """Tests for get_fund_sector_allocation."""

    async def test_success(self):
        mock_info = {
            "sectorWeightings": {"tech": 0.4, "finance": 0.3},
            "bondRatings": {"AAA": 0.5, "BBB": 0.2},
            # other keys can be missing
        }
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result_str = await funds.get_fund_sector_allocation("FSKAX")
            mock_yf_ticker.assert_called_once_with("FSKAX")
            result_json = json.loads(result_str)
            assert result_json["sectorWeightings"]["tech"] == 0.4
            assert result_json["bondRatings"]["AAA"] == 0.5
            assert result_json["bondHoldings"] == {}  # Default for missing key
            assert result_json["stockHoldings"] == {}  # Default for missing key

    async def test_yfinance_exception(self):
        with patch("yfinance.Ticker", side_effect=Exception("YF Sector Error")):
            result_str = await funds.get_fund_sector_allocation("ERROR_TICKER")
            result_json = json.loads(result_str)
            assert "error" in result_json
            assert "Failed to get sector allocation: YF Sector Error" in result_json["error"]


@pytest.mark.asyncio
class TestGetFundPerformance:
    """Tests for get_fund_performance."""

    async def test_success(self):
        mock_info = {
            "ytdReturn": 0.05,
            "oneYearReturn": 0.10,
            "threeYearAverageReturn": 0.08,
            "alpha": 0.01,
            "beta": 0.95,
        }
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_info

        with patch("yfinance.Ticker", return_value=mock_ticker_instance) as mock_yf_ticker:
            result_str = await funds.get_fund_performance("FXAIX")
            mock_yf_ticker.assert_called_once_with("FXAIX")
            result_json = json.loads(result_str)
            assert result_json["ytdReturn"] == 0.05
            assert result_json["alpha"] == 0.01
            assert result_json["fiveYearAverageReturn"] is None  # Missing key

    async def test_yfinance_exception(self):
        with patch("yfinance.Ticker", side_effect=Exception("YF Perf Error")):
            result_str = await funds.get_fund_performance("ERROR_TICKER")
            result_json = json.loads(result_str)
            assert "error" in result_json
            assert "Failed to get fund performance: YF Perf Error" in result_json["error"]


@pytest.mark.asyncio
class TestCompareFunds:
    """Tests for compare_funds."""

    async def test_compare_two_funds_success(self):
        mock_info_vbtlx = {
            "longName": "Vanguard Total Bond Market Index Fund",
            "annualReportExpenseRatio": 0.05,
            "yield": 0.02,
            "ytdReturn": 0.01,
            "threeYearAverageReturn": 0.005,
            "fiveYearAverageReturn": 0.015,
            "totalAssets": 3.0e11,
            "beta": None,  # Beta might be None for bond funds
            "morningStarOverallRating": 4,
        }
        mock_info_vtsax = {
            "longName": "Vanguard Total Stock Market Index Fund",
            "annualReportExpenseRatio": 0.0004,
            "yield": 0.013,
            "ytdReturn": 0.12,
            "threeYearAverageReturn": 0.10,
            "fiveYearAverageReturn": 0.11,
            "totalAssets": 1.2e12,
            "beta": 1.01,
            "morningStarOverallRating": 5,
        }

        mock_vbtlx_ticker = MagicMock()
        mock_vbtlx_ticker.info = mock_info_vbtlx
        mock_vtsax_ticker = MagicMock()
        mock_vtsax_ticker.info = mock_info_vtsax

        # Use side_effect to return different mock_ticker_instances for different tickers
        def ticker_side_effect(ticker_arg):
            if ticker_arg == "VBTLX":
                return mock_vbtlx_ticker
            if ticker_arg == "VTSAX":
                return mock_vtsax_ticker
            raise ValueError("Unexpected ticker in test")

        with patch("yfinance.Ticker", side_effect=ticker_side_effect) as mock_yf_ticker:
            result_str = await funds.compare_funds(["VBTLX", "VTSAX"])
            result_json = json.loads(result_str)

            assert mock_yf_ticker.call_count == 2
            assert "fund_comparison" in result_json
            assert len(result_json["fund_comparison"]) == 2

            fund1_data = result_json["fund_comparison"][0]
            assert fund1_data["symbol"] == "VBTLX"
            assert fund1_data["name"] == mock_info_vbtlx["longName"]
            assert fund1_data["expenseRatio"] == mock_info_vbtlx["annualReportExpenseRatio"]

            fund2_data = result_json["fund_comparison"][1]
            assert fund2_data["symbol"] == "VTSAX"
            assert fund2_data["name"] == mock_info_vtsax["longName"]
            assert fund2_data["beta"] == mock_info_vtsax["beta"]

    async def test_compare_empty_list(self):
        with patch("yfinance.Ticker") as mock_yf_ticker:  # Should not be called
            result_str = await funds.compare_funds([])
            result_json = json.loads(result_str)
            assert result_json == {"fund_comparison": []}
            mock_yf_ticker.assert_not_called()

    async def test_compare_with_one_ticker_failing(self):
        mock_info_vtsax = {"longName": "Vanguard Total Stock Market Index Fund", "annualReportExpenseRatio": 0.0004}
        mock_vtsax_ticker = MagicMock()
        mock_vtsax_ticker.info = mock_info_vtsax

        def ticker_side_effect(ticker_arg):
            if ticker_arg == "GOOD":
                return mock_vtsax_ticker
            if ticker_arg == "BAD":
                raise Exception("Simulated yfinance error for BAD ticker")
            raise ValueError(f"Unexpected ticker in side_effect: {ticker_arg}")

        with patch("yfinance.Ticker", side_effect=ticker_side_effect) as mock_yf_ticker:
            result_str = await funds.compare_funds(["GOOD", "BAD"])
            result_json = json.loads(result_str)

            # The entire comparison fails if one ticker errors out, as per current implementation
            assert "error" in result_json
            assert "Failed to compare funds: Simulated yfinance error for BAD ticker" in result_json["error"]
            # yf.Ticker would be called for "GOOD", then for "BAD" which raises.
            assert mock_yf_ticker.call_count == 2


class TestRegisterFundTools:
    """Tests for the register() function in funds plugin."""

    def test_register_tools(self):
        mock_mcp = MagicMock()
        mock_actual_decorator = MagicMock(side_effect=lambda f: f)
        mock_mcp.tool.return_value = mock_actual_decorator

        funds.register(mock_mcp)

        expected_tool_names = [
            "get_fund_profile",
            "get_fund_holdings",
            "get_fund_sector_allocation",
            "get_fund_performance",
            "compare_funds",
        ]

        assert mock_mcp.tool.call_count == len(expected_tool_names)

        actual_registered_tool_names = sorted(
            [call_obj[0][0].__name__ for call_obj in mock_actual_decorator.call_args_list]
        )
        assert actual_registered_tool_names == sorted(expected_tool_names)

        for func_name in actual_registered_tool_names:
            assert not func_name.startswith("_")
            assert func_name != "register_fund_tools"


if __name__ == "__main__":
    pytest.main([__file__])
