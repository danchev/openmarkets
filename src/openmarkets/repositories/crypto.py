from abc import ABC, abstractmethod

import yfinance as yf

from openmarkets.core.constants import DEFAULT_SENTIMENT_TICKERS, TOP_CRYPTO_TICKERS
from openmarkets.schemas.crypto import CryptoFastInfo, CryptoHistory


class ICryptoRepository(ABC):
    @abstractmethod
    def fetch_crypto_info(self, ticker: str) -> CryptoFastInfo:
        pass

    @abstractmethod
    def fetch_crypto_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> list[CryptoHistory]:
        pass

    @abstractmethod
    def fetch_top_cryptocurrencies(self, count: int = 10) -> list[CryptoFastInfo]:
        pass

    @abstractmethod
    def fetch_crypto_fear_greed_proxy(self, tickers: list[str] | None = None) -> str:
        pass


class YFinanceCryptoRepository(ICryptoRepository):
    """Repository for fetching crypto data from yfinance."""

    def fetch_crypto_info(self, ticker: str) -> CryptoFastInfo:
        if not ticker.endswith("-USD"):
            ticker += "-USD"
        fast_info = yf.Ticker(ticker).fast_info
        return CryptoFastInfo(**fast_info)

    def fetch_crypto_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> list[CryptoHistory]:
        if not ticker.endswith("-USD"):
            ticker += "-USD"
        df = yf.Ticker(ticker).history(period=period, interval=interval)
        df.reset_index(inplace=True)
        return [CryptoHistory(**row.to_dict()) for _, row in df.iterrows()]

    def fetch_top_cryptocurrencies(self, count: int = 10) -> list[CryptoFastInfo]:
        selected_cryptos = TOP_CRYPTO_TICKERS[: min(count, 20)]
        return [self.fetch_crypto_info(crypto) for crypto in selected_cryptos]

    def fetch_crypto_fear_greed_proxy(self, tickers: list[str] | None = None) -> dict:
        if tickers is None:
            tickers = DEFAULT_SENTIMENT_TICKERS
        try:
            sentiment_data = []
            total_change = 0
            valid_cryptos = 0
            for crypto in tickers:
                ticker = yf.Ticker(crypto)
                hist = ticker.history(period="7d")
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
            return {
                "sentiment_proxy": sentiment,
                "average_weekly_change": avg_change,
                "crypto_data": sentiment_data,
                "note": "This is a simplified sentiment proxy based on price movements, not the official Fear & Greed Index",
            }
        except Exception as e:
            return {"error": f"Failed to calculate sentiment proxy: {str(e)}"}
