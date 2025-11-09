# print("DEBUG_MODULE_LOAD: corporate_actions.py -- V2 --") # Test print
"""Corporate actions and dividend tools for yfinance MCP server."""

import inspect
import sys
from datetime import datetime

import pandas as pd
import yfinance as yf
from mcp.server import FastMCP


async def get_dividends_summary(
    symbol: str,
    period: str = "1y",
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """Get dividend history for a stock.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
        period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)

    Returns:
        Dictionary containing dividend data
    """
    try:
        ticker = yf.Ticker(symbol)

        if start_date and end_date:
            dividends = ticker.dividends.loc[start_date:end_date]
        else:
            history_df = ticker.history(period=period)
            dividends = history_df["Dividends"] if "Dividends" in history_df else pd.Series(dtype="float64")

        # Filter out zero dividends
        dividends = dividends[dividends > 0]

        return {
            "symbol": symbol,
            "dividends": dividends.to_dict(),
            "total_dividends": float(dividends.sum()),
            "dividend_count": len(dividends),
            "period": period if not (start_date and end_date) else f"{start_date} to {end_date}",
        }
    except Exception as e:
        return {"error": str(e)}


async def get_splits_summary(symbol: str, period: str = "20y") -> dict:
    """Get stock split history.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
        period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')

    Returns:
        Dictionary containing stock split data
    """
    try:
        ticker = yf.Ticker(symbol)
        splits = ticker.splits

        # Filter splits within the period
        if period != "max":
            history = ticker.history(period=period)
            # print(f"DEBUG_FUNC: Inside get_splits, history.empty = {history.empty}")  # Removed debug print
            if not history.empty:
                start_date = history.index[0]
                if not splits.empty:  # Avoid TypeError on empty index comparison
                    splits = splits[splits.index >= start_date]

        debug_len_before_return = len(splits)
        return {"symbol": symbol, "splits": splits.to_dict(), "split_count": debug_len_before_return, "period": period}
    except Exception as e:
        return {"error": str(e)}


async def get_actions(symbol: str, period: str = "1y") -> dict:
    """Get all corporate actions (dividends and splits) for a stock.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
        period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')

    Returns:
        Dictionary containing all corporate actions
    """
    try:
        ticker = yf.Ticker(symbol)
        actions = ticker.actions

        # Filter actions within the period
        if period != "max":
            history = ticker.history(period=period)
            if not history.empty:
                start_date = history.index[0]
                if not actions.empty:  # Avoid TypeError on empty index comparison
                    actions = actions[actions.index >= start_date]

        return {"symbol": symbol, "actions": actions.to_dict(), "period": period, "total_actions": len(actions)}
    except Exception as e:
        # print(f"ERROR in get_actions for {symbol}: {e} (type: {type(e)})") # Removed
        return {"error": str(e)}


async def get_dividend_yield(symbol: str) -> dict:
    """Calculate dividend yield and related metrics.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')

    Returns:
        Dictionary containing dividend yield metrics
    """

    def convert_unix_to_date(timestamp):
        """Helper function to convert Unix timestamp to ISO 8601 date."""
        if timestamp:
            return datetime.fromtimestamp(timestamp).isoformat()
        return None

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Get trailing twelve months dividends
        dividends = ticker.dividends
        if len(dividends) > 0:
            # Get dividends from last 12 months
            # Ensure the index is a DatetimeIndex
            if not isinstance(dividends.index, pd.DatetimeIndex):
                dividends.index = pd.to_datetime(dividends.index)
            latest_date = dividends.index[-1]
            one_year_ago = latest_date - pd.DateOffset(years=1)
            ttm_dividends = dividends[dividends.index > one_year_ago].sum()
        else:
            ttm_dividends = 0

        current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
        dividend_yield = (ttm_dividends / current_price * 100) if current_price > 0 else 0

        return {
            "symbol": symbol,
            "current_price": current_price,
            "ttm_dividends": float(ttm_dividends),
            "dividend_yield_percent": round(dividend_yield, 2),
            "forward_dividend_rate": info.get("dividendRate"),
            "forward_dividend_yield": info.get("dividendYield"),
            "payout_ratio": info.get("payoutRatio"),
            "ex_dividend_date": convert_unix_to_date(info.get("exDividendDate")),
            "dividend_date": convert_unix_to_date(info.get("dividendDate")),
        }
    except Exception as e:
        # print(f"ERROR in get_dividend_yield for {symbol}: {e} (type: {type(e)})") # Removed
        return {"error": str(e)}


def register(mcp: FastMCP):
    module = sys.modules[__name__]
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or name == "register":
            continue
        mcp.tool()(func)
