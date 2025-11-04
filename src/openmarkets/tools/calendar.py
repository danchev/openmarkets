"""Calendar and events tools."""

import inspect
import json
import sys
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf
from mcp.server import FastMCP

from openmarkets.core.serializers import JSONSerializer


async def get_earnings_calendar(ticker: str) -> str:
    """Get earnings calendar information.

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing earnings calendar data
    """
    stock = yf.Ticker(ticker)
    calendar = stock.calendar
    if isinstance(calendar, dict):
        return json.dumps(calendar, indent=2, default=str)
    elif isinstance(calendar, pd.DataFrame) and not calendar.empty:
        return json.dumps(calendar.to_dict(orient="records"), indent=2, cls=JSONSerializer)
    return json.dumps({"error": "No earnings calendar data available"})


async def get_earnings_dates(ticker: str) -> str:
    """Get upcoming and past earnings dates.

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing earnings dates
    """

    def convert_unix_to_date(timestamp):
        """Helper function to convert Unix timestamp to ISO 8601 date with timezone info (UTC)."""
        if timestamp:
            return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
        return None

    stock = yf.Ticker(ticker)
    info = stock.info

    earnings_info = {
        "earningsTimestamp": convert_unix_to_date(info.get("earningsTimestamp")),
        "exDividendDate": convert_unix_to_date(info.get("exDividendDate")),
        "dividendDate": convert_unix_to_date(info.get("dividendDate")),
    }

    return json.dumps(earnings_info, indent=2, default=str)


async def get_market_calendar_info(ticker: str) -> str:
    """Get market calendar information for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing market calendar info
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    market_info = {
        "exchange": info.get("exchange"),
        "exchangeTimezoneName": info.get("exchangeTimezoneName"),
        "exchangeTimezoneShortName": info.get("exchangeTimezoneShortName"),
        "gmtOffSetMilliseconds": info.get("gmtOffSetMilliseconds"),
        "market": info.get("market"),
        "marketState": info.get("marketState"),
        "regularMarketTime": info.get("regularMarketTime"),
        "regularMarketPreviousClose": info.get("regularMarketPreviousClose"),
        "preMarketPrice": info.get("preMarketPrice"),
        "preMarketTime": info.get("preMarketTime"),
        "postMarketPrice": info.get("postMarketPrice"),
        "postMarketTime": info.get("postMarketTime"),
    }

    return json.dumps(market_info, indent=2, default=str)


def register(mcp: FastMCP):
    module = sys.modules[__name__]
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or name == "register":
            continue
        mcp.tool()(func)
