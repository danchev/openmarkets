"""Cryptocurrency and alternative assets tools."""

import inspect
import json
import sys

import yfinance as yf
from mcp.server import FastMCP


async def get_crypto_info(crypto_symbol: str) -> str:
    """Get cryptocurrency information.

    Args:
        crypto_symbol: Crypto symbol with -USD suffix (e.g., 'BTC-USD', 'ETH-USD')

    Returns:
        JSON string containing crypto information
    """
    if not crypto_symbol.endswith("-USD"):
        crypto_symbol += "-USD"

    crypto = yf.Ticker(crypto_symbol)
    info = crypto.info

    crypto_info = {
        "symbol": info.get("symbol"),
        "name": info.get("shortName"),
        "currentPrice": info.get("currentPrice"),
        "marketCap": info.get("marketCap"),
        "volume24Hr": info.get("volume24Hr"),
        "circulatingSupply": info.get("circulatingSupply"),
        "maxSupply": info.get("maxSupply"),
        "previousClose": info.get("previousClose"),
        "dayLow": info.get("dayLow"),
        "dayHigh": info.get("dayHigh"),
        "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
        "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
        "currency": info.get("currency"),
    }

    return json.dumps(crypto_info, indent=2)


async def get_crypto_historical_data(crypto_symbol: str, period: str = "1mo", interval: str = "1d") -> str:
    """Get historical cryptocurrency data.

    Args:
        crypto_symbol: Crypto symbol with -USD suffix (e.g., 'BTC-USD')
        period: Data period (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max)
        interval: Data interval (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)

    Returns:
        JSON string containing historical crypto data
    """
    if not crypto_symbol.endswith("-USD"):
        crypto_symbol += "-USD"

    crypto = yf.Ticker(crypto_symbol)
    hist = crypto.history(period=period, interval=interval)

    if hist.empty:
        return json.dumps({"error": "No historical data available"})

    return hist.to_json(date_format="iso")


async def get_top_cryptocurrencies(count: int = 10) -> str:
    """Get data for top cryptocurrencies by market cap.

    Args:
        count: Number of top cryptocurrencies to return (max 20)

    Returns:
        JSON string containing top crypto data
    """
    # Top cryptocurrencies by market cap (approximate list)
    top_cryptos = [
        "BTC-USD",
        "ETH-USD",
        "BNB-USD",
        "XRP-USD",
        "SOL-USD",
        "ADA-USD",
        "AVAX-USD",
        "DOGE-USD",
        "TRX-USD",
        "DOT-USD",
        "MATIC-USD",
        "LTC-USD",
        "SHIB-USD",
        "BCH-USD",
        "UNI-USD",
        "ATOM-USD",
        "LINK-USD",
        "ETC-USD",
        "XLM-USD",
        "ALGO-USD",
    ]

    selected_cryptos = top_cryptos[: min(count, 20)]
    crypto_data = []

    try:
        for crypto in selected_cryptos:
            ticker = yf.Ticker(crypto)
            info = ticker.info
            hist = ticker.history(period="2d")

            daily_change = None
            daily_change_percent = None

            if len(hist) >= 2:
                current_price = hist.iloc[-1]["Close"]
                previous_close = hist.iloc[-2]["Close"]
                daily_change = current_price - previous_close
                daily_change_percent = (daily_change / previous_close) * 100

            # Ensure data types are JSON serializable
            current_price_val = info.get("currentPrice")
            market_cap_val = info.get("marketCap")
            volume_val = info.get("volume")

            crypto_data.append(
                {
                    "symbol": crypto,
                    "name": info.get("shortName", ""),
                    "currentPrice": float(current_price_val) if current_price_val is not None else None,
                    "marketCap": int(market_cap_val) if market_cap_val is not None else None,
                    "volume": int(volume_val) if volume_val is not None else None,
                    "dailyChange": float(daily_change) if daily_change is not None else None,
                    "dailyChangePercent": float(daily_change_percent) if daily_change_percent is not None else None,
                }
            )

        return json.dumps({"count": len(crypto_data), "cryptocurrencies": crypto_data}, indent=2)

    except Exception as e:
        # print(f"ERROR in get_top_cryptocurrencies: {e} (type: {type(e)})") # Removed final error print
        return json.dumps({"error": f"Failed to get crypto data: {str(e)}"})


async def get_crypto_fear_greed_proxy(crypto_symbols: list[str] = None) -> str:
    """Get a proxy for crypto market sentiment using price movements.

    Args:
        crypto_symbols: List of crypto symbols to analyze (default: major cryptos)

    Returns:
        JSON string containing market sentiment proxy data
    """
    if crypto_symbols is None:
        crypto_symbols = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "SOL-USD"]

    try:
        sentiment_data = []
        total_change = 0
        valid_cryptos = 0

        for crypto in crypto_symbols:
            ticker = yf.Ticker(crypto)
            hist = ticker.history(period="7d")  # Get 7 days for weekly change

            if len(hist) >= 2:
                weekly_change = ((hist.iloc[-1]["Close"] - hist.iloc[0]["Close"]) / hist.iloc[0]["Close"]) * 100
                daily_change = ((hist.iloc[-1]["Close"] - hist.iloc[-2]["Close"]) / hist.iloc[-2]["Close"]) * 100

                sentiment_data.append(
                    {
                        "symbol": crypto,
                        "daily_change_percent": daily_change,
                        "weekly_change_percent": weekly_change,
                    }
                )

                total_change += weekly_change
                valid_cryptos += 1

        # Simple sentiment scoring (this is a basic proxy)
        avg_change = total_change / valid_cryptos if valid_cryptos > 0 else 0

        if avg_change > 10:
            sentiment = "Extreme Greed"
        elif avg_change > 5:
            sentiment = "Greed"
        elif avg_change > 0:
            sentiment = "Neutral-Positive"
        elif avg_change > -5:
            sentiment = "Neutral-Negative"
        elif avg_change > -10:
            sentiment = "Fear"
        else:
            sentiment = "Extreme Fear"

        return json.dumps(
            {
                "sentiment_proxy": sentiment,
                "average_weekly_change": avg_change,
                "crypto_data": sentiment_data,
                "note": "This is a simplified sentiment proxy based on price movements, not the official Fear & Greed Index",
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": f"Failed to calculate sentiment proxy: {str(e)}"})


def register(mcp: FastMCP):
    """Register cryptocurrency tools with the MCP server."""
    module = sys.modules[__name__]
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or name == "register":
            continue
        mcp.tool()(func)
