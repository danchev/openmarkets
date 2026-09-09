"""Synthetic provider prices through MCP dispatch, computation and serialization."""

import numpy as np
import pandas as pd
import pytest
from mcp import Client
from mcp.server import MCPServer

from openmarkets.services.portfolio import PortfolioService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def portfolio_server(monkeypatch):
    benchmark = np.tile([-0.01, 0.01], 60)
    rf = 1.1 ** (1 / 252) - 1
    returns = pd.DataFrame(
        {
            "TAIL": [-0.1] + [-0.02] * 11 + [0.01] * 108,
            "SPY": benchmark,
            "ALPHA": 2 * benchmark - rf,
            "CASH": np.zeros(120),
            "QQQ": np.tile([0.02, -0.005, 0.01], 40),
            "IWM": np.tile([0.005, -0.01, 0.015, 0.0], 30),
            "TLT": np.tile([0.001, 0.002, -0.001, -0.002, 0.0], 24),
            "GLD": np.tile([0.002, -0.001], 60),
        }
    )
    prices = pd.DataFrame(
        np.vstack([np.ones(len(returns.columns)), np.cumprod(1 + returns.to_numpy(), axis=0)]) * 100,
        columns=returns.columns,
        index=pd.date_range("2024-01-01", periods=121, freq="B"),
    )
    calls = []

    class Ticker:
        def __init__(self, ticker, session=None):
            self.ticker = ticker

        def history(self, **kwargs):
            calls.append(kwargs)
            assert kwargs["auto_adjust"] is True
            assert kwargs["interval"] == "1d"
            return prices[[self.ticker]].rename(columns={self.ticker: "Close"})

    def download(tickers, **kwargs):
        calls.append(kwargs)
        assert kwargs["auto_adjust"] is True
        assert kwargs["interval"] == "1d"
        return pd.concat({"Close": prices[tickers]}, axis=1)

    monkeypatch.setattr("openmarkets.repositories.portfolio.yf.Ticker", Ticker)
    monkeypatch.setattr("openmarkets.repositories.portfolio.yf.download", download)
    server = MCPServer("Portfolio formula validation")
    PortfolioService().register_tool_methods(server)
    return server, prices, calls


async def test_tail_risk_and_zero_alpha_cross_mcp_boundary(portfolio_server):
    server, _, _ = portfolio_server
    async with Client(server) as client:
        tail = await client.call_tool("calculate_portfolio_risk_metrics", {"tickers": ["TAIL"], "risk_free_rate": 0})
        assert tail.is_error is False
        # Six observations in the 5% tail: -10% plus five -2% returns.
        assert tail.structured_content["cvar_95_percent"] == -3.33
        assert tail.structured_content["cvar_99_percent"] == -8.67
        alpha = await client.call_tool(
            "calculate_portfolio_risk_metrics", {"tickers": ["ALPHA"], "risk_free_rate": 0.1}
        )
        assert alpha.is_error is False
        assert alpha.structured_content["alpha_percent"] == 0.0
        assert alpha.structured_content["beta"] == 2.0


@pytest.mark.parametrize("tickers,weights", [(["TAIL", "CASH"], [0.0, 100.0]), (["CASH"], [100.0])])
async def test_zero_variance_allocation_serializes_null_attribution(portfolio_server, tickers, weights):
    server, _, _ = portfolio_server
    async with Client(server) as client:
        result = await client.call_tool("calculate_minimum_variance_portfolio", {"tickers": tickers})
        assert result.is_error is False
        allocations = result.structured_content["allocations"]
        assert [row["weight_percent"] for row in allocations] == weights
        assert all(row["risk_contribution_percent"] is None for row in allocations)


@pytest.mark.parametrize(
    "tool,kwargs,warmup",
    [
        ("backtest_trend_following_strategy", {"fast_window": 1, "slow_window": 2}, 2),
        ("backtest_mean_reversion_strategy", {"rsi_window": 2}, 3),
    ],
)
async def test_backtest_evaluation_metadata_survives_repository_and_mcp(portfolio_server, tool, kwargs, warmup):
    server, prices, _ = portfolio_server
    async with Client(server) as client:
        result = await client.call_tool(tool, {"ticker": "TAIL", **kwargs})
        assert result.is_error is False
        body = result.structured_content
        assert body["evaluation_start"] == str(prices.index[0].date())
        assert body["evaluation_end"] == str(prices.index[-1].date())
        assert body["warmup_observations"] == warmup
        assert body["buy_and_hold_return_percent"] == round((prices["TAIL"].iloc[-1] / 100 - 1) * 100, 2)


async def test_model_and_rate_contracts_advertised_and_enforced(portfolio_server):
    server, _, calls = portfolio_server
    async with Client(server) as client:
        listing = await client.list_tools()
        tools = {tool.name: tool for tool in listing.tools}
        rate_schema = tools["calculate_portfolio_risk_metrics"].input_schema["properties"]["risk_free_rate"]
        assert rate_schema["exclusiveMinimum"] == -1
        assert "raw-return intercept" in tools["calculate_factor_exposures"].description
        result = await client.call_tool("calculate_portfolio_risk_metrics", {"tickers": ["TAIL"], "risk_free_rate": -1})
        assert result.is_error is True
        assert calls == []  # Rejected before fetching provider data.
        factors = await client.call_tool("calculate_factor_exposures", {"ticker": "ALPHA"})
        assert factors.is_error is False
        assert factors.structured_content["exposures"][0]["factor"] == "Annualized Raw-Return Intercept"
