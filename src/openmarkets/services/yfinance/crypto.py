import json

import yfinance as yf

from openmarkets.schemas.crypto import CryptoFastInfo, CryptoHistory


def fetch_crypto_info(ticker: str) -> CryptoFastInfo:
    """Get cryptocurrency information.

    Args:
        ticker: Crypto symbol with -USD suffix (e.g., 'BTC-USD', 'ETH-USD')

    Returns:
        JSON string containing crypto information
    """
    if not ticker.endswith("-USD"):
        ticker += "-USD"

    fast_info = yf.Ticker(ticker).fast_info
    return CryptoFastInfo(**fast_info)


def fetch_crypto_history(ticker: str, period: str = "1y", interval: str = "1d") -> list[CryptoHistory]:
    """
    Fetch historical OHLCV data for a given crypto ticker.

        Args:
        ticker: Crypto symbol with -USD suffix (e.g., 'BTC-USD', 'ETH-USD')

    Returns:
        List of CryptoHistory objects containing historical data
    """
    if not ticker.endswith("-USD"):
        ticker += "-USD"

    df = yf.Ticker(ticker).history(period=period, interval=interval)
    df.reset_index(inplace=True)
    return [CryptoHistory(**row.to_dict()) for _, row in df.iterrows()]


def fetch_top_cryptocurrencies(count: int = 10) -> list[dict]:
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
            market_cap_val = info.get("marketCap")
            volume_val = info.get("volume")

            crypto_data.append(
                {
                    "symbol": crypto,
                    "name": info.get("shortName", ""),
                    "currentPrice": float(current_price) if current_price is not None else None,
                    "marketCap": int(market_cap_val) if market_cap_val is not None else None,
                    "volume": int(volume_val) if volume_val is not None else None,
                    "dailyChange": float(daily_change) if daily_change is not None else None,
                    "dailyChangePercent": float(daily_change_percent) if daily_change_percent is not None else None,
                }
            )

        return crypto_data

    except Exception as e:
        raise RuntimeError(f"Failed to fetch top cryptocurrencies: {str(e)}") from e


def fetch_crypto_fear_greed_proxy(tickers: list[str] | None = None) -> str:
    """Get a proxy for crypto market sentiment using price movements.

    Args:
        tickers: List of crypto symbols to analyze (default: major cryptos)

    Returns:
        JSON string containing market sentiment proxy data
    """
    if tickers is None:
        tickers = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "SOL-USD"]

    try:
        sentiment_data = []
        total_change = 0
        valid_cryptos = 0

        for crypto in tickers:
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
