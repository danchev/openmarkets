"""Market data and trending tools."""

import inspect
import json
import sys

import yfinance as yf
from mcp.server import FastMCP

from openmarkets.core.serializers import JSONSerializer


async def get_available_markets() -> list:
    """Get a list of available markets.

    Returns:
        List of market names
    """
    # Note: yfinance doesn't have a direct endpoint for available markets
    # This is a simplified implementation using major US indices
    return ["US", "GB", "ASIA", "EUROPE", "RATES", "COMMODITIES", "CURRENCIES", "CRYPTOCURRENCIES"]


async def get_market_status(market: str) -> str:
    """Get current market status and trading hours.

    Returns:
        JSON string containing market status information
    """
    # Note: yfinance doesn't have a direct market status endpoint
    # This is a simplified implementation using a major index
    try:
        market = yf.Market(market)
        status = market.status

        return json.dumps(status, indent=2, default=str, cls=JSONSerializer)
    except Exception as e:
        return json.dumps({"error": f"Failed to get market status: {str(e)}"})


async def get_market_summary(market: str) -> str:
    """Get current market summary information.

    Returns:
        JSON string containing market summary information
    """
    # Note: yfinance doesn't have a direct market summary endpoint
    # This is a simplified implementation using a major index
    try:
        market = yf.Market(market)
        summary = market.summary

        return json.dumps(summary, indent=2, default=str, cls=JSONSerializer)
    except Exception as e:
        return json.dumps({"error": f"Failed to get market summary: {str(e)}"})


async def get_sector_performance() -> str:
    """Get sector performance using sector ETFs.

    Returns:
        JSON string containing sector performance data
    """
    sector_etfs = {
        "Technology": "XLK",
        "Healthcare": "XLV",
        "Financials": "XLF",
        "Consumer Discretionary": "XLY",
        "Communication Services": "XLC",
        "Industrials": "XLI",
        "Consumer Staples": "XLP",
        "Energy": "XLE",
        "Utilities": "XLU",
        "Real Estate": "XLRE",
        "Materials": "XLB",
    }

    try:
        sector_performance = []

        for sector, etf in sector_etfs.items():
            stock = yf.Ticker(etf)
            info = stock.info
            hist = stock.history(period="2d")

            if len(hist) >= 2:
                daily_change = ((hist.iloc[-1]["Close"] - hist.iloc[-2]["Close"]) / hist.iloc[-2]["Close"]) * 100
            else:
                daily_change = None

            sector_performance.append(
                {
                    "sector": sector,
                    "etf_symbol": etf,
                    "current_price": info.get("currentPrice"),
                    "daily_change_percent": daily_change,
                    "volume": info.get("volume"),
                }
            )

        return json.dumps({"sector_performance": sector_performance}, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to get sector performance: {str(e)}"})


async def get_index_data(indices: list[str] = None) -> str:
    """Get major market indices data.

    Args:
        indices: List of index symbols (default: major US indices)

    Returns:
        JSON string containing index data
    """
    if indices is None:
        indices = ["^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX"]

    index_names = {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones Industrial Average",
        "^IXIC": "NASDAQ Composite",
        "^RUT": "Russell 2000",
        "^VIX": "CBOE Volatility Index",
    }

    try:
        index_data = []

        for index in indices:
            stock = yf.Ticker(index)
            hist = stock.history(period="2d")

            if len(hist) >= 2:
                current_price = hist.iloc[-1]["Close"]
                previous_close = hist.iloc[-2]["Close"]
                daily_change = current_price - previous_close
                daily_change_percent = (daily_change / previous_close) * 100
            else:
                current_price = None
                daily_change = None
                daily_change_percent = None

            index_data.append(
                {
                    "symbol": index,
                    "name": index_names.get(index, index),
                    "current_price": current_price,
                    "daily_change": daily_change,
                    "daily_change_percent": daily_change_percent,
                    "volume": hist.iloc[-1]["Volume"] if len(hist) > 0 else None,
                }
            )

        return json.dumps({"indices": index_data}, indent=2, cls=JSONSerializer)

    except Exception as e:
        return json.dumps({"error": f"Failed to get index data: {str(e)}"})


def register(mcp: FastMCP):
    """Register market data tools with the MCP server."""
    module = sys.modules[__name__]
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or name == "register":
            continue
        mcp.tool()(func)
