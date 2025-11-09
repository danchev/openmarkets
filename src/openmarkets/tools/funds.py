"""Mutual funds and ETF tools for yfinance MCP server."""

import inspect
import json
import sys
from datetime import datetime

import yfinance as yf
from mcp.server import FastMCP


async def get_fund_profile(ticker: str) -> str:
    """Get mutual fund or ETF profile information.

    Args:
        ticker: Fund ticker symbol

    Returns:
        JSON string containing fund profile data
    """

    def convert_unix_to_date(timestamp):
        """Helper function to convert Unix timestamp to ISO 8601 date."""
        if timestamp:
            return datetime.fromtimestamp(timestamp).isoformat()
        return None

    try:
        fund = yf.Ticker(ticker)
        info = fund.info

        fund_profile = {
            "symbol": info.get("symbol"),
            "longName": info.get("longName"),
            "fundFamily": info.get("fundFamily"),
            "category": info.get("category"),
            "fundInceptionDate": convert_unix_to_date(info.get("fundInceptionDate")),
            "totalAssets": info.get("totalAssets"),
            "netExpenseRatio": info.get("annualReportExpenseRatio"),
            "beta3Year": info.get("beta3Year"),
            "yield": info.get("yield"),
            "ytdReturn": info.get("ytdReturn"),  # FIX: ytdReturn is a percentage
            "threeYearAverageReturn": info.get("threeYearAverageReturn"),
            "fiveYearAverageReturn": info.get("fiveYearAverageReturn"),
            "morningStarRiskRating": info.get("morningStarRiskRating"),
            "morningStarOverallRating": info.get("morningStarOverallRating"),
            "currency": info.get("currency"),
            "navPrice": info.get("navPrice"),
        }

        return json.dumps(fund_profile, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": f"Failed to get fund profile: {str(e)}"})


async def get_fund_holdings(ticker: str, count: int = 20) -> str:
    """Get fund top holdings.

    Args:
        ticker: Fund ticker symbol
        count: Number of top holdings to return

    Returns:
        JSON string containing fund holdings data
    """
    try:
        fund = yf.Ticker(ticker)

        # Try to get fund holdings from info
        info = fund.info
        holdings = info.get("holdings", [])

        if holdings:
            limited_holdings = holdings[:count]
            return json.dumps({"symbol": ticker, "top_holdings": limited_holdings}, indent=2)
        else:
            return json.dumps({"error": "No holdings data available for this fund"})
    except Exception as e:
        return json.dumps({"error": f"Failed to get fund holdings: {str(e)}"})


async def get_fund_sector_allocation(ticker: str) -> str:
    """Get fund sector allocation.

    Args:
        ticker: Fund ticker symbol

    Returns:
        JSON string containing sector allocation data
    """
    try:
        fund = yf.Ticker(ticker)
        info = fund.info

        sector_allocation = {
            "sectorWeightings": info.get("sectorWeightings", {}),
            "bondRatings": info.get("bondRatings", {}),
            "bondHoldings": info.get("bondHoldings", {}),
            "stockHoldings": info.get("stockHoldings", {}),
        }

        return json.dumps(sector_allocation, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to get sector allocation: {str(e)}"})


async def get_fund_performance(ticker: str) -> str:
    """Get fund performance metrics.

    Args:
        ticker: Fund ticker symbol

    Returns:
        JSON string containing performance data
    """
    try:
        fund = yf.Ticker(ticker)
        info = fund.info

        performance = {
            "ytdReturn": info.get("ytdReturn"),
            "oneYearReturn": info.get("oneYearReturn"),
            "threeYearAverageReturn": info.get("threeYearAverageReturn"),
            "fiveYearAverageReturn": info.get("fiveYearAverageReturn"),
            "tenYearAverageReturn": info.get("tenYearAverageReturn"),
            "alpha": info.get("alpha"),
            "beta": info.get("beta"),
            "rSquared": info.get("rSquared"),
            "standardDeviation": info.get("standardDeviation"),
            "sharpeRatio": info.get("sharpeRatio"),
            "treynorRatio": info.get("treynorRatio"),
        }

        return json.dumps(performance, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to get fund performance: {str(e)}"})


async def compare_funds(tickers: list[str]) -> str:
    """Compare multiple funds side by side.

    Args:
        tickers: List of fund ticker symbols

    Returns:
        JSON string containing comparison data
    """
    try:
        comparison_data = []

        for ticker in tickers:
            fund = yf.Ticker(ticker)
            info = fund.info

            fund_data = {
                "symbol": ticker,
                "name": info.get("longName"),
                "expenseRatio": info.get("annualReportExpenseRatio"),
                "yield": info.get("yield"),
                "ytdReturn": info.get("ytdReturn"),
                "threeYearReturn": info.get("threeYearAverageReturn"),
                "fiveYearReturn": info.get("fiveYearAverageReturn"),
                "totalAssets": info.get("totalAssets"),
                "beta": info.get("beta"),
                "morningstarRating": info.get("morningStarOverallRating"),
            }

            comparison_data.append(fund_data)

        return json.dumps({"fund_comparison": comparison_data}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to compare funds: {str(e)}"})


def register(mcp: FastMCP):
    module = sys.modules[__name__]
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or name == "register":
            continue
        mcp.tool()(func)
