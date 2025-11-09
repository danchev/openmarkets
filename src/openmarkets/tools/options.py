"""Options trading tools."""

import inspect
import json
import sys

import yfinance as yf
from mcp.server import FastMCP

from openmarkets.core.serializers import JSONSerializer


async def get_options_expiration_dates(ticker: str) -> str:
    """Get available options expiration dates.

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing expiration dates
    """
    stock = yf.Ticker(ticker)
    try:
        expirations = stock.options
        return json.dumps({"expiration_dates": list(expirations)}, cls=JSONSerializer)
    except Exception as e:
        return json.dumps({"error": f"No options data available: {str(e)}"})


async def get_option_chain(ticker: str, expiration_date: str | None = None) -> str:
    """Get options chain data for a specific expiration date.

    Args:
        ticker: Stock ticker symbol
        expiration_date: Expiration date in YYYY-MM-DD format (if None, uses nearest expiration)

    Returns:
        JSON string containing options chain data
    """
    try:
        stock = yf.Ticker(ticker)
        if expiration_date:
            option_chain = stock.option_chain(expiration_date)
        else:
            # Use the first available expiration date
            expirations = stock.options
            if not expirations:
                return json.dumps({"error": "No options data available"})
            option_chain = stock.option_chain(expirations[0])

        result = {
            "calls": option_chain.calls.to_dict("records") if hasattr(option_chain, "calls") else [],
            "puts": option_chain.puts.to_dict("records") if hasattr(option_chain, "puts") else [],
        }

        return json.dumps(result, indent=2, cls=JSONSerializer)
    except Exception as e:
        return json.dumps({"error": f"Failed to get options data: {str(e)}"})


async def get_options_volume_analysis(ticker: str, expiration_date: str | None = None) -> str:
    """Get options volume and open interest analysis.

    Args:
        ticker: Stock ticker symbol
        expiration_date: Expiration date in YYYY-MM-DD format (if None, uses nearest expiration)

    Returns:
        JSON string containing volume analysis
    """
    try:
        stock = yf.Ticker(ticker)
        if expiration_date:
            option_chain = stock.option_chain(expiration_date)
        else:
            # Use the first available expiration date
            expirations = stock.options
            if not expirations:
                return json.dumps({"error": "No options data available"})
            option_chain = stock.option_chain(expirations[0])

        calls = option_chain.calls
        puts = option_chain.puts

        analysis = {
            "total_call_volume": calls["volume"].sum() if "volume" in calls.columns else 0,
            "total_put_volume": puts["volume"].sum() if "volume" in puts.columns else 0,
            "total_call_open_interest": calls["openInterest"].sum() if "openInterest" in calls.columns else 0,
            "total_put_open_interest": puts["openInterest"].sum() if "openInterest" in puts.columns else 0,
            "put_call_ratio_volume": (puts["volume"].sum() / calls["volume"].sum())
            if "volume" in calls.columns and calls["volume"].sum() > 0
            else None,
            "put_call_ratio_oi": (puts["openInterest"].sum() / calls["openInterest"].sum())
            if "openInterest" in calls.columns and calls["openInterest"].sum() > 0
            else None,
        }

        return json.dumps(analysis, indent=2, cls=JSONSerializer)
    except Exception as e:
        return json.dumps({"error": f"Failed to analyze options data: {str(e)}"})


async def get_options_by_moneyness(
    ticker: str,
    expiration_date: str | None = None,
    moneyness_range: float = 0.1,
) -> str:
    """Get options filtered by moneyness (proximity to current stock price).

    Args:
        ticker: Stock ticker symbol
        expiration_date: Expiration date in YYYY-MM-DD format (if None, uses nearest expiration)
        moneyness_range: Range around current price (e.g., 0.1 for ±10%)

    Returns:
        JSON string containing filtered options data
    """
    try:
        stock = yf.Ticker(ticker)
        current_price = stock.info.get("currentPrice")
        if not current_price:
            return json.dumps({"error": "Could not get current stock price"})

        if expiration_date:
            option_chain = stock.option_chain(expiration_date)
        else:
            # Use the first available expiration date
            expirations = stock.options
            if not expirations:
                return json.dumps({"error": "No options data available"})
            option_chain = stock.option_chain(expirations[0])

        price_min = current_price * (1 - moneyness_range)
        price_max = current_price * (1 + moneyness_range)

        calls = option_chain.calls
        puts = option_chain.puts

        filtered_calls = calls[(calls["strike"] >= price_min) & (calls["strike"] <= price_max)]
        filtered_puts = puts[(puts["strike"] >= price_min) & (puts["strike"] <= price_max)]

        result = {
            "current_price": current_price,
            "price_range": {"min": price_min, "max": price_max},
            "calls": filtered_calls.to_dict("records"),
            "puts": filtered_puts.to_dict("records"),
        }

        return json.dumps(result, indent=2, cls=JSONSerializer)
    except Exception as e:
        return json.dumps({"error": f"Failed to filter options data: {str(e)}"})


async def get_options_skew(ticker: str, expiration_date: str | None = None) -> str:
    """Analyze and return the volatility skew for call and put options.

    This function retrieves the implied volatility for each strike price of both call and put options
    for a given stock ticker and expiration date. If no expiration date is provided, the nearest available
    expiration is used. The result is a JSON string containing lists of strike/implied volatility pairs
    for calls and puts, which can be used to visualize or analyze the volatility skew.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL').
        expiration_date: Expiration date in 'YYYY-MM-DD' format. If None, uses the nearest expiration.

    Returns:
        JSON string with two keys:
            - "call_skew": List of dicts with 'strike' and 'impliedVolatility' for call options.
            - "put_skew": List of dicts with 'strike' and 'impliedVolatility' for put options.
        If data is unavailable or an error occurs, returns a JSON string with an "error" key.
    """
    try:
        stock = yf.Ticker(ticker)

        # If no expiration date is provided, use the nearest available expiration
        if not expiration_date:
            expirations = stock.options
            if not expirations:
                return json.dumps({"error": "No options data available for this ticker."})
            expiration_date = expirations[0]

        option_chain = stock.option_chain(expiration_date)
        # Check if option chain data is available and not empty
        if not option_chain or (option_chain.calls.empty and option_chain.puts.empty):
            return json.dumps({"error": f"No options data available for {ticker} on {expiration_date}."})

        call_skew = []
        if not option_chain.calls.empty:
            # Ensure required columns are present in calls DataFrame
            if "strike" not in option_chain.calls.columns or "impliedVolatility" not in option_chain.calls.columns:
                return json.dumps({"error": "Missing 'strike' or 'impliedVolatility' in call options data."})
            call_skew = option_chain.calls[["strike", "impliedVolatility"]].to_dict("records")

        put_skew = []
        if not option_chain.puts.empty:
            # Ensure required columns are present in puts DataFrame
            if "strike" not in option_chain.puts.columns or "impliedVolatility" not in option_chain.puts.columns:
                return json.dumps({"error": "Missing 'strike' or 'impliedVolatility' in put options data."})
            put_skew = option_chain.puts[["strike", "impliedVolatility"]].to_dict("records")

        result = {
            "call_skew": call_skew,
            "put_skew": put_skew,
        }

        return json.dumps(result, indent=2, cls=JSONSerializer)
    except Exception as e:
        # Catch and report any errors from yfinance or data processing
        return json.dumps({"error": f"Failed to get volatility skew analysis: {str(e)}"})


def register(mcp: FastMCP):
    """Register options tools with the MCP server."""
    module = sys.modules[__name__]
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or name == "register":
            continue
        mcp.tool()(func)
