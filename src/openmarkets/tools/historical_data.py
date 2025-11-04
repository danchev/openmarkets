"""Historical data tools."""

import inspect
import json
import sys

import yfinance as yf
from mcp.server import FastMCP


async def get_historical_data(ticker: str, period: str = "1mo", interval: str = "1d") -> str:
    """Get historical price data for a stock.

    Args:
        ticker: Stock ticker symbol
        period: Data period (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max)
        interval: Data interval (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)

    Returns:
        JSON string containing historical price data
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    return hist.to_json(date_format="iso")


async def get_intraday_data(ticker: str, period: str = "1d", interval: str = "5m") -> str:
    """Get intraday historical data with short intervals.

    Args:
        ticker: Stock ticker symbol
        period: Data period (1d,5d for intraday data)
        interval: Data interval (1m,2m,5m,15m,30m,60m,90m)

    Returns:
        JSON string containing intraday historical data
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    return hist.to_json(date_format="iso")


async def get_prepost_market_data(ticker: str, period: str = "1d") -> str:
    """Get pre and post market data.

    Args:
        ticker: Stock ticker symbol
        period: Data period

    Returns:
        JSON string containing pre/post market data
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, prepost=True)
    return hist.to_json(date_format="iso")


async def get_dividends(ticker: str) -> str:
    """Get dividend history for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing dividend history
    """
    stock = yf.Ticker(ticker)
    dividends = stock.dividends
    if dividends is not None and not dividends.empty:
        return dividends.to_json(date_format="iso")
    return json.dumps({"error": "No dividend data available"})


async def get_splits(ticker: str) -> str:
    """Get stock split history.

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing stock split history
    """
    stock = yf.Ticker(ticker)
    splits = stock.splits
    if splits is not None and not splits.empty:
        return splits.to_json(date_format="iso")
    return json.dumps({"error": "No stock split data available"})


async def get_capital_gains(ticker: str) -> str:
    """Get capital gains history (mainly for mutual funds).

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing capital gains history
    """
    stock = yf.Ticker(ticker)
    capital_gains = stock.capital_gains
    if capital_gains is not None and not capital_gains.empty:
        return capital_gains.to_json(date_format="iso")
    return json.dumps({"error": "No capital gains data available"})


def register(mcp: FastMCP):
    module = sys.modules[__name__]
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or name == "register":
            continue
        mcp.tool()(func)
