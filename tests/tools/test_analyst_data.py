"""
Unit tests for openmarkets.tools.analyst_data plugin functions.

These tests cover recommendations, price targets, and tool registration logic.
"""

import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from openmarkets.tools.analyst_data import (
    get_analyst_price_targets,
    get_recommendations,
    register,
)


@pytest.fixture
def mock_ticker():
    """Fixture to mock the yfinance.Ticker object."""
    mock = MagicMock()
    mock.info = {}
    return mock


@pytest.mark.asyncio
async def test_get_recommendations_success(mock_ticker):
    """Test get_recommendations returns correct JSON for valid data."""
    data = {"Firm": ["A", "B"], "To Grade": ["Buy", "Hold"]}
    df = pd.DataFrame(data)
    mock_ticker.recommendations = df
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_recommendations("AAPL")
        assert json.loads(result) == json.loads(df.to_json(date_format="iso"))


@pytest.mark.asyncio
async def test_get_recommendations_no_data(mock_ticker):
    """Test get_recommendations returns error when no data is available."""
    mock_ticker.recommendations = None
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_recommendations("AAPL")
        assert json.loads(result) == {"error": "No recommendations available"}


@pytest.mark.asyncio
async def test_get_analyst_price_targets_success(mock_ticker):
    """Test get_analyst_price_targets returns correct JSON for valid data."""
    info_data = {
        "targetHighPrice": 200,
        "targetLowPrice": 100,
        "targetMeanPrice": 150,
        "targetMedianPrice": 140,
        "recommendationMean": 2.0,
        "recommendationKey": "buy",
        "numberOfAnalystOpinions": 10,
    }
    mock_ticker.info = info_data
    with patch("yfinance.Ticker", return_value=mock_ticker):
        result = await get_analyst_price_targets("AAPL")
        assert json.loads(result) == info_data


def test_register_analyst_data_tools():
    """Test that register() registers all public async functions as tools."""
    mock_mcp = MagicMock()
    mock_mcp.tool = MagicMock()
    register(mock_mcp)
    expected_calls = [get_recommendations, get_analyst_price_targets]
    registered_funcs = [call_args[0][0] for call_args in mock_mcp.tool.return_value.call_args_list]
    assert len(registered_funcs) == len(expected_calls)
    for func in expected_calls:
        assert func in registered_funcs
