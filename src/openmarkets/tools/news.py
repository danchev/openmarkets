"""News and events tools for yfinance MCP server."""

import inspect
import json
import sys

import yfinance as yf
from mcp.server import FastMCP


async def get_news(ticker: str, count: int = 10) -> str:
    """Get latest news for a stock.

    Args:
        ticker: Stock ticker symbol
        count: Number of news articles to return (max 50)

    Returns:
        JSON string containing news articles
    """
    try:
        stock = yf.Ticker(ticker)
        news = stock.news

        if news:
            # Limit to requested count
            limited_news = news[: min(count, 50)]
            return json.dumps({"symbol": ticker, "news_count": len(limited_news), "news": limited_news}, indent=2)
        else:
            return json.dumps({"error": "No news available for this ticker"})
    except Exception as e:
        return json.dumps({"error": f"Failed to get news: {str(e)}"})


async def get_fast_info(ticker: str) -> str:
    """Get fast info (quick basic data) for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing fast info data. The returned JSON includes the following fields:
            - currency: Trading currency (e.g., "USD")
            - dayHigh: Highest price of the day (float)
            - dayLow: Lowest price of the day (float)
            - exchange: Exchange code (e.g., "NMS")
            - fiftyDayAverage: 50-day average price (float)
            - lastPrice: Last traded price (float)
            - lastVolume: Last traded volume (int)
            - marketCap: Market capitalization (float)
            - open: Opening price of the day (float)
            - previousClose: Previous closing price (float)
            - quoteType: Type of security (e.g., "EQUITY")
            - regularMarketPreviousClose: Previous close in regular market (float)
            - shares: Number of shares outstanding (int)
            - tenDayAverageVolume: 10-day average trading volume (int)
            - threeMonthAverageVolume: 3-month average trading volume (int)
            - timezone: Timezone of the exchange (e.g., "America/New_York")
            - twoHundredDayAverage: 200-day average price (float)
            - yearChange: Change in price over the past year (float, as a ratio)
            - yearHigh: Highest price in the past year (float)
            - yearLow: Lowest price in the past year (float)
    """
    try:
        stock = yf.Ticker(ticker)
        fast_info = stock.fast_info

        if fast_info:
            return json.dumps(dict(fast_info), indent=2)
        else:
            return json.dumps({"error": "No fast info available"})
    except Exception as e:
        return json.dumps({"error": f"Failed to get fast info: {str(e)}"})


async def get_shares_outstanding(ticker: str, start_date: str | None = None, end_date: str | None = None) -> str:
    """Get shares outstanding data over time.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)

    Returns:
        JSON string containing shares outstanding data
    """
    try:
        stock = yf.Ticker(ticker)

        if start_date and end_date:
            shares = stock.get_shares_full(start=start_date, end=end_date)
        else:
            shares = stock.get_shares_full()

        if shares is not None and not shares.empty:
            return json.dumps({"symbol": ticker, "shares_outstanding": shares.to_dict()}, indent=2)
        else:
            return json.dumps({"error": "No shares outstanding data available"})
    except Exception as e:
        return json.dumps({"error": f"Failed to get shares outstanding: {str(e)}"})


async def get_insider_purchases(ticker: str) -> str:
    """Get insider purchase data.

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing insider purchase data
    """
    try:
        stock = yf.Ticker(ticker)
        insider_purchases = stock.insider_purchases

        if insider_purchases is not None and not insider_purchases.empty:
            return insider_purchases.to_json(date_format="iso")
        else:
            return json.dumps({"error": "No insider purchase data available"})
    except Exception as e:
        return json.dumps({"error": f"Failed to get insider purchases: {str(e)}"})


async def get_insider_roster_holders(ticker: str) -> str:
    """Get insider roster holders data.

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing insider roster data
    """
    try:
        stock = yf.Ticker(ticker)
        insider_roster = stock.insider_roster_holders

        if insider_roster is not None and not insider_roster.empty:
            return insider_roster.to_json(date_format="iso")
        else:
            return json.dumps({"error": "No insider roster data available"})
    except Exception as e:
        return json.dumps({"error": f"Failed to get insider roster: {str(e)}"})


async def get_insider_transactions(ticker: str) -> str:
    """Get insider transaction data.

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing insider transaction data
    """
    try:
        stock = yf.Ticker(ticker)
        insider_transactions = stock.insider_transactions

        if insider_transactions is not None and not insider_transactions.empty:
            return insider_transactions.to_json(date_format="iso")
        else:
            return json.dumps({"error": "No insider transaction data available"})
    except Exception as e:
        return json.dumps({"error": f"Failed to get insider transactions: {str(e)}"})


def register(mcp: FastMCP):
    """Register news and events tools with the MCP server."""
    module = sys.modules[__name__]
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or name == "register":
            continue
        mcp.tool()(func)
