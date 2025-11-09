import json
from datetime import date

import yfinance as yf

from openmarkets.core.serializers import JSONSerializer
from openmarkets.schemas.options import (
    CallOption,
    OptionContractChain,
    OptionExpirationDate,
    OptionUnderlying,
    PutOption,
)


def fetch_option_expiration_dates(ticker: str) -> list[OptionExpirationDate]:
    """
    Fetch the option expiration dates for a given ticker and return as a list of OptionExpirationDate.
    """
    options = yf.Ticker(ticker).options
    return [OptionExpirationDate(date=dt) for dt in options]


def fetch_option_chain(ticker: str, expiration: date | None = None) -> OptionContractChain:
    """
    Fetch the option chain for a given ticker and return as an OptionContractChain.
    """
    option_chain = yf.Ticker(ticker).option_chain(date=str(expiration) if expiration else None)
    calls = option_chain.calls
    puts = option_chain.puts
    call_objs = [CallOption(**row.to_dict()) for _, row in calls.iterrows()] if not calls.empty else None
    put_objs = [PutOption(**row.to_dict()) for _, row in puts.iterrows()] if not puts.empty else None
    underlying = OptionUnderlying(**getattr(option_chain, "underlying", {}))
    return OptionContractChain(calls=call_objs, puts=put_objs, underlying=underlying)


def fetch_call_options(ticker: str, expiration: date | None = None) -> list[CallOption] | None:
    """
    Fetch the call options for a given ticker and expiration date, and return as a list of CallOption.
    """

    option_chain = yf.Ticker(ticker).option_chain(str(expiration) if expiration else None)
    calls = option_chain.calls
    if calls.empty:
        return None
    return [CallOption(**row.to_dict()) for _, row in calls.iterrows()]


def fetch_put_options(ticker: str, expiration: date | None = None) -> list[PutOption] | None:
    """
    Fetch the put options for a given ticker and expiration date, and return as a list of PutOption.
    """
    option_chain = yf.Ticker(ticker).option_chain(str(expiration) if expiration else None)
    puts = option_chain.puts
    if puts.empty:
        return None
    return [PutOption(**row.to_dict()) for _, row in puts.iterrows()]


def fetch_options_volume_analysis(ticker: str, expiration_date: str | None = None) -> str:
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


async def fetch_options_by_moneyness(
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


async def fetch_options_skew(ticker: str, expiration_date: str | None = None) -> str:
    """
    Analyze and return the volatility skew for call and put options.

    Retrieves the implied volatility for each strike price of both call and put options
    for a given stock ticker and expiration date. If no expiration date is provided, the nearest available
    expiration is used. Returns a JSON string with two keys:
        - "call_skew": List of dicts with 'strike' and 'impliedVolatility' for call options.
        - "put_skew": List of dicts with 'strike' and 'impliedVolatility' for put options.
    If data is unavailable or an error occurs, returns a JSON string with an "error" key.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL').
        expiration_date (Optional[str]): Expiration date in 'YYYY-MM-DD' format. If None, uses the nearest expiration.

    Returns:
        str: JSON string with volatility skew data or error message.
    """
    try:
        stock = yf.Ticker(ticker)

        if not expiration_date:
            expirations = stock.options
            if not expirations:
                return json.dumps({"error": "No options data available for this ticker."})
            expiration_date = expirations[0]

        option_chain = stock.option_chain(expiration_date)
        if not option_chain or (option_chain.calls.empty and option_chain.puts.empty):
            return json.dumps({"error": f"No options data available for {ticker} on {expiration_date}."})

        call_skew = []
        if not option_chain.calls.empty:
            if "strike" not in option_chain.calls.columns or "impliedVolatility" not in option_chain.calls.columns:
                return json.dumps({"error": "Missing 'strike' or 'impliedVolatility' in call options data."})
            call_skew = option_chain.calls[["strike", "impliedVolatility"]].to_dict("records")

        put_skew = []
        if not option_chain.puts.empty:
            if "strike" not in option_chain.puts.columns or "impliedVolatility" not in option_chain.puts.columns:
                return json.dumps({"error": "Missing 'strike' or 'impliedVolatility' in put options data."})
            put_skew = option_chain.puts[["strike", "impliedVolatility"]].to_dict("records")

        result = {
            "call_skew": call_skew,
            "put_skew": put_skew,
        }

        return json.dumps(result, indent=2, cls=JSONSerializer)
    except Exception as e:
        return json.dumps({"error": f"Failed to get volatility skew analysis: {str(e)}"})
