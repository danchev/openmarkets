from abc import ABC, abstractmethod

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.core.constants import DEFAULT_SENTIMENT_TICKERS, TOP_CRYPTO_TICKERS
from openmarkets.schemas.crypto import CryptoFastInfo, CryptoHistory


class ICryptoRepository(ABC):
    @abstractmethod
    def get_crypto_info(self, ticker: str, session: Session | None = None) -> CryptoFastInfo:
        pass

    @abstractmethod
    def get_crypto_history(
        self, ticker: str, period: str = "1y", interval: str = "1d", session: Session | None = None
    ) -> list[CryptoHistory]:
        pass

    @abstractmethod
    def get_top_cryptocurrencies(self, count: int = 10, session: Session | None = None) -> list[CryptoFastInfo]:
        pass

    @abstractmethod
    def get_crypto_fear_greed_proxy(self, tickers: list[str] | None = None, session: Session | None = None) -> dict:
        pass


class YFinanceCryptoRepository(ICryptoRepository):
    """Repository for fetching crypto data from yfinance."""

    def get_crypto_info(self, ticker: str, session: Session | None = None) -> CryptoFastInfo:
        if not ticker.endswith("-USD"):
            ticker += "-USD"
        fast_info = yf.Ticker(ticker, session=session).fast_info
        return CryptoFastInfo(**fast_info)

    def get_crypto_history(
        self, ticker: str, period: str = "1y", interval: str = "1d", session: Session | None = None
    ) -> list[CryptoHistory]:
        if period not in ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"):
            raise ValueError("Invalid period. Must be one of: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.")
        if interval not in ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"):
            raise ValueError(
                "Invalid interval. Must be one of: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo."
            )
        if not ticker.endswith("-USD"):
            ticker += "-USD"
        df = yf.Ticker(ticker, session=session).history(period=period, interval=interval)
        df.reset_index(inplace=True)
        return [CryptoHistory(**row.to_dict()) for _, row in df.iterrows()]

    def get_top_cryptocurrencies(self, count: int = 10, session: Session | None = None) -> list[CryptoFastInfo]:
        selected_cryptos = TOP_CRYPTO_TICKERS[: min(count, 20)]
        # reuse get_crypto_info and forward session
        return [self.get_crypto_info(crypto, session=session) for crypto in selected_cryptos]

    def get_crypto_fear_greed_proxy(self, tickers: list[str] | None = None, session: Session | None = None) -> dict:
        if tickers is None:
            tickers = DEFAULT_SENTIMENT_TICKERS
        try:
            sentiment_data = []
            total_change = 0
            valid_cryptos = 0
            for crypto in tickers:
                ticker = yf.Ticker(crypto, session=session)
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
