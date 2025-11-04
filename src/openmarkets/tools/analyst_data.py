"""Analyst data tools."""

import inspect
import json
import sys

import yfinance as yf
from mcp.server import FastMCP


async def get_recommendations(ticker: str) -> str:
    """Get analyst recommendations for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing analyst recommendations
    """
    stock = yf.Ticker(ticker)
    recs = stock.recommendations
    if recs is not None and not recs.empty:
        return recs.to_json(date_format="iso")
    return json.dumps({"error": "No recommendations available"})


async def get_analyst_price_targets(ticker: str) -> str:
    """Get analyst price targets and estimates.

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing price targets
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    price_targets = {
        "targetHighPrice": info.get("targetHighPrice"),
        "targetLowPrice": info.get("targetLowPrice"),
        "targetMeanPrice": info.get("targetMeanPrice"),
        "targetMedianPrice": info.get("targetMedianPrice"),
        "recommendationMean": info.get("recommendationMean"),
        "recommendationKey": info.get("recommendationKey"),
        "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions"),
    }
    return json.dumps(price_targets, indent=2)


def register(mcp: FastMCP):
    """Register all public async callables in this module as tools."""
    module = sys.modules[__name__]
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or name == "register":
            continue
        mcp.tool()(func)
