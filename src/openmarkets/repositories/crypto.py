"""Repository layer for cryptocurrency data operations.

Provides abstractions and implementations for fetching cryptocurrency
information, historical data, and sentiment indicators.
"""

from abc import ABC, abstractmethod

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.core.constants import DEFAULT_SENTIMENT_TICKERS, TOP_CRYPTO_TICKERS
from openmarkets.schemas.crypto import CryptoFastInfo, CryptoHistory


class ICryptoRepository(ABC):
    """Abstract interface for cryptocurrency data repositories."""

    @abstractmethod
    def get_crypto_info(self, ticker: str, session: Session | None = None) -> CryptoFastInfo:
        """Retrieve fast info for a cryptocurrency.

        Args:
            ticker: Cryptocurrency symbol (e.g., 'BTC', 'ETH').
            session: Optional HTTP session for request handling.

        Returns:
            Fast info data for the cryptocurrency.
        """
        pass

    @abstractmethod
    def get_crypto_history(
        self, ticker: str, period: str = "1y", interval: str = "1d", session: Session | None = None
    ) -> list[CryptoHistory]:
        """Retrieve historical price data for a cryptocurrency.

        Args:
            ticker: Cryptocurrency symbol.
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max).
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo).
            session: Optional HTTP session for request handling.

        Returns:
            List of historical data points.
        """
        pass

    @abstractmethod
    def get_top_cryptocurrencies(self, count: int = 10, session: Session | None = None) -> list[CryptoFastInfo]:
        """Retrieve top cryptocurrencies by market cap.

        Args:
            count: Number of cryptocurrencies to retrieve (max 20).
            session: Optional HTTP session for request handling.

        Returns:
            List of top cryptocurrencies.
        """
        pass

    @abstractmethod
    def get_crypto_fear_greed_proxy(self, tickers: list[str] | None = None, session: Session | None = None) -> dict:
        """Calculate a sentiment proxy based on cryptocurrency price movements.

        Args:
            tickers: List of cryptocurrency symbols. Uses defaults if None.
            session: Optional HTTP session for request handling.

        Returns:
            Dictionary containing sentiment analysis and supporting data.
        """
        pass


class YFinanceCryptoRepository(ICryptoRepository):
    """Repository for fetching crypto data from yfinance."""

    def get_crypto_info(self, ticker: str, session: Session | None = None) -> CryptoFastInfo:
        """Retrieve fast info for a cryptocurrency.

        Args:
            ticker: Cryptocurrency symbol (e.g., 'BTC', 'ETH').
            session: Optional HTTP session for request handling.

        Returns:
            Fast info data for the cryptocurrency.
        """
        normalized_ticker = self._normalize_ticker(ticker)
        ticker_obj = yf.Ticker(normalized_ticker, session=session)
        fast_info = ticker_obj.fast_info
        return CryptoFastInfo(**fast_info)

    def get_crypto_history(
        self, ticker: str, period: str = "1y", interval: str = "1d", session: Session | None = None
    ) -> list[CryptoHistory]:
        """Retrieve historical price data for a cryptocurrency.

        Args:
            ticker: Cryptocurrency symbol.
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max).
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo).
            session: Optional HTTP session for request handling.

        Returns:
            List of historical data points.

        Raises:
            ValueError: If period or interval is invalid.
        """
        self._validate_period(period)
        self._validate_interval(interval)
        normalized_ticker = self._normalize_ticker(ticker)
        ticker_obj = yf.Ticker(normalized_ticker, session=session)
        dataframe = ticker_obj.history(period=period, interval=interval)
        dataframe.reset_index(inplace=True)
        return self._convert_dataframe_to_history(dataframe)

    def get_top_cryptocurrencies(self, count: int = 10, session: Session | None = None) -> list[CryptoFastInfo]:
        """Retrieve top cryptocurrencies by market cap.

        Args:
            count: Number of cryptocurrencies to retrieve (max 20).
            session: Optional HTTP session for request handling.

        Returns:
            List of top cryptocurrencies.
        """
        selected_cryptos = TOP_CRYPTO_TICKERS[: min(count, 20)]
        return [self.get_crypto_info(crypto, session=session) for crypto in selected_cryptos]

    def get_crypto_fear_greed_proxy(self, tickers: list[str] | None = None, session: Session | None = None) -> dict:
        """Calculate a sentiment proxy based on cryptocurrency price movements.

        Args:
            tickers: List of cryptocurrency symbols. Uses defaults if None.
            session: Optional HTTP session for request handling.

        Returns:
            Dictionary containing sentiment analysis and supporting data.
        """
        tickers = tickers or DEFAULT_SENTIMENT_TICKERS
        try:
            sentiment_data = self._collect_crypto_sentiment_data(tickers, session)
            average_change = self._calculate_average_weekly_change(sentiment_data)
            sentiment_label = self._determine_sentiment_label(average_change)
            return self._build_sentiment_response(sentiment_label, average_change, sentiment_data)
        except Exception as error:
            return {"error": f"Failed to calculate sentiment proxy: {str(error)}"}

    def _normalize_ticker(self, ticker: str) -> str:
        """Normalize cryptocurrency ticker to include -USD suffix.

        Args:
            ticker: Cryptocurrency symbol.

        Returns:
            Normalized ticker with -USD suffix.
        """
        if ticker.endswith("-USD"):
            return ticker
        return f"{ticker}-USD"

    def _validate_period(self, period: str) -> None:
        """Validate the period parameter.

        Args:
            period: Time period to validate.

        Raises:
            ValueError: If period is invalid.
        """
        valid_periods = ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
        if period not in valid_periods:
            raise ValueError(f"Invalid period. Must be one of: {', '.join(valid_periods)}.")

    def _validate_interval(self, interval: str) -> None:
        """Validate the interval parameter.

        Args:
            interval: Data interval to validate.

        Raises:
            ValueError: If interval is invalid.
        """
        valid_intervals = ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo")
        if interval not in valid_intervals:
            raise ValueError(f"Invalid interval. Must be one of: {', '.join(valid_intervals)}.")

    def _convert_dataframe_to_history(self, dataframe) -> list[CryptoHistory]:
        """Convert pandas DataFrame to list of CryptoHistory objects.

        Args:
            dataframe: Pandas DataFrame containing historical data.

        Returns:
            List of CryptoHistory objects.
        """
        return [CryptoHistory(**row.to_dict()) for _, row in dataframe.iterrows()]

    def _collect_crypto_sentiment_data(self, tickers: list[str], session: Session | None) -> list[dict]:
        """Collect sentiment data for given cryptocurrency tickers.

        Args:
            tickers: List of cryptocurrency symbols.
            session: Optional HTTP session for request handling.

        Returns:
            List of dictionaries containing sentiment data per crypto.
        """
        sentiment_data = []
        for crypto in tickers:
            crypto_data = self._fetch_crypto_sentiment(crypto, session)
            if crypto_data:
                sentiment_data.append(crypto_data)
        return sentiment_data

    def _fetch_crypto_sentiment(self, crypto: str, session: Session | None) -> dict | None:
        """Fetch sentiment data for a single cryptocurrency.

        Args:
            crypto: Cryptocurrency symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Dictionary with sentiment data or None if insufficient history.
        """
        ticker_obj = yf.Ticker(crypto, session=session)
        history = ticker_obj.history(period="7d")
        if len(history) < 2:
            return None
        weekly_change = self._calculate_weekly_change(history)
        daily_change = self._calculate_daily_change(history)
        return {
            "symbol": crypto,
            "daily_change_percent": daily_change,
            "weekly_change_percent": weekly_change,
        }

    def _calculate_weekly_change(self, history) -> float:
        """Calculate weekly percentage change from history data.

        Args:
            history: Historical price data DataFrame.

        Returns:
            Weekly percentage change.
        """
        first_close = history.iloc[0]["Close"]
        last_close = history.iloc[-1]["Close"]
        return ((last_close - first_close) / first_close) * 100

    def _calculate_daily_change(self, history) -> float:
        """Calculate daily percentage change from history data.

        Args:
            history: Historical price data DataFrame.

        Returns:
            Daily percentage change.
        """
        previous_close = history.iloc[-2]["Close"]
        last_close = history.iloc[-1]["Close"]
        return ((last_close - previous_close) / previous_close) * 100

    def _calculate_average_weekly_change(self, sentiment_data: list[dict]) -> float:
        """Calculate average weekly change from sentiment data.

        Args:
            sentiment_data: List of sentiment data dictionaries.

        Returns:
            Average weekly percentage change.
        """
        if not sentiment_data:
            return 0.0
        total_change = sum(data["weekly_change_percent"] for data in sentiment_data)
        return total_change / len(sentiment_data)

    def _determine_sentiment_label(self, average_change: float) -> str:
        """Determine sentiment label based on average weekly change.

        Args:
            average_change: Average weekly percentage change.

        Returns:
            Sentiment label string.
        """
        if average_change > 10:
            return "Extreme Greed"
        if average_change > 5:
            return "Greed"
        if average_change > 0:
            return "Neutral-Positive"
        if average_change > -5:
            return "Neutral-Negative"
        if average_change > -10:
            return "Fear"
        return "Extreme Fear"

    def _build_sentiment_response(
        self, sentiment_label: str, average_change: float, sentiment_data: list[dict]
    ) -> dict:
        """Build the final sentiment response dictionary.

        Args:
            sentiment_label: Determined sentiment label.
            average_change: Average weekly percentage change.
            sentiment_data: List of sentiment data dictionaries.

        Returns:
            Complete sentiment response dictionary.
        """
        return {
            "sentiment_proxy": sentiment_label,
            "average_weekly_change": average_change,
            "crypto_data": sentiment_data,
            "note": "This is a simplified sentiment proxy based on price movements, not the official Fear & Greed Index",
        }
