"""Technical analysis repository interfaces and implementations.

This module provides repositories for retrieving technical analysis data
including indicators, volatility metrics, and support/resistance levels.
"""

from abc import ABC, abstractmethod

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.schemas.technical_analysis import (
    SupportResistanceLevelsDict,
    TechnicalIndicatorsDict,
    VolatilityMetricsDict,
)


class ITechnicalAnalysisRepository(ABC):
    """Interface for technical analysis data repositories."""

    @abstractmethod
    def get_technical_indicators(
        self, ticker: str, period: str = "6mo", session: Session | None = None
    ) -> TechnicalIndicatorsDict:
        """Retrieve technical indicators for a given ticker.

        Args:
            ticker: Stock ticker symbol.
            period: Historical data period (default: "6mo").
            session: Optional curl_cffi session for requests.

        Returns:
            Dictionary containing technical indicators.
        """
        pass

    @abstractmethod
    def get_volatility_metrics(
        self, ticker: str, period: str = "1y", session: Session | None = None
    ) -> VolatilityMetricsDict:
        """Retrieve volatility metrics for a given ticker.

        Args:
            ticker: Stock ticker symbol.
            period: Historical data period (default: "1y").
            session: Optional curl_cffi session for requests.

        Returns:
            Dictionary containing volatility metrics.
        """
        pass

    @abstractmethod
    def get_support_resistance_levels(
        self, ticker: str, period: str = "6mo", session: Session | None = None
    ) -> SupportResistanceLevelsDict:
        """Retrieve support and resistance levels for a given ticker.

        Args:
            ticker: Stock ticker symbol.
            period: Historical data period (default: "6mo").
            session: Optional curl_cffi session for requests.

        Returns:
            Dictionary containing support and resistance levels.
        """
        pass


class YFinanceTechnicalAnalysisRepository(ITechnicalAnalysisRepository):
    """YFinance-based implementation of technical analysis repository."""

    def get_technical_indicators(
        self, ticker: str, period: str = "6mo", session: Session | None = None
    ) -> TechnicalIndicatorsDict:
        """Retrieve technical indicators for a given ticker.

        Args:
            ticker: Stock ticker symbol.
            period: Historical data period (default: "6mo").
            session: Optional curl_cffi session for requests.

        Returns:
            Dictionary containing technical indicators including price,
            52-week high/low, moving averages, and volume.

        Raises:
            ValueError: If no historical data is available for the ticker.
        """
        stock = yf.Ticker(ticker, session=session)
        hist = stock.history(period=period)

        if hist.empty:
            raise ValueError("No historical data available")

        current_price = hist["Close"].iloc[-1]
        high_52w = hist["High"].max()
        low_52w = hist["Low"].min()
        avg_volume = hist["Volume"].mean()

        sma_20 = self._calculate_sma(hist, window=20)
        sma_50 = self._calculate_sma(hist, window=50)
        sma_200 = self._calculate_sma(hist, window=200)

        price_position = self._calculate_price_position(current_price, low_52w, high_52w)

        return self._build_indicators_dict(
            current_price=current_price,
            high_52w=high_52w,
            low_52w=low_52w,
            avg_volume=avg_volume,
            price_position=price_position,
            sma_20=sma_20,
            sma_50=sma_50,
            sma_200=sma_200,
        )

    def _calculate_sma(self, hist, window: int) -> float | None:
        """Calculate simple moving average for given window.

        Args:
            hist: Historical price data DataFrame.
            window: Number of periods for moving average.

        Returns:
            Simple moving average value or None if insufficient data.
        """
        if len(hist) < window:
            return None
        return hist["Close"].rolling(window=window).mean().iloc[-1]

    def _calculate_price_position(self, current_price: float, low: float, high: float) -> float | None:
        """Calculate price position within 52-week range.

        Args:
            current_price: Current stock price.
            low: 52-week low.
            high: 52-week high.

        Returns:
            Price position as percentage or None if range is zero.
        """
        price_range = high - low
        if price_range == 0:
            return None
        return ((current_price - low) / price_range) * 100

    def _calculate_price_vs_sma(self, current_price: float, sma: float | None) -> float | None:
        """Calculate price difference from moving average.

        Args:
            current_price: Current stock price.
            sma: Simple moving average value.

        Returns:
            Percentage difference or None if SMA is unavailable.
        """
        if sma is None:
            return None
        if sma == 0:
            return None
        return ((current_price - sma) / sma) * 100

    def _build_indicators_dict(
        self,
        current_price: float,
        high_52w: float,
        low_52w: float,
        avg_volume: float,
        price_position: float | None,
        sma_20: float | None,
        sma_50: float | None,
        sma_200: float | None,
    ) -> TechnicalIndicatorsDict:
        """Build technical indicators dictionary.

        Args:
            current_price: Current stock price.
            high_52w: 52-week high.
            low_52w: 52-week low.
            avg_volume: Average trading volume.
            price_position: Price position in 52-week range.
            sma_20: 20-day simple moving average.
            sma_50: 50-day simple moving average.
            sma_200: 200-day simple moving average.

        Returns:
            Dictionary containing all technical indicators.
        """
        return {
            "current_price": float(current_price),
            "fifty_two_week_high": float(high_52w),
            "fifty_two_week_low": float(low_52w),
            "price_position_in_52w_range_percent": (float(price_position) if price_position is not None else None),
            "average_volume": float(avg_volume),
            "sma_20": float(sma_20) if sma_20 is not None else None,
            "sma_50": float(sma_50) if sma_50 is not None else None,
            "sma_200": float(sma_200) if sma_200 is not None else None,
            "price_vs_sma_20": self._calculate_price_vs_sma(current_price, sma_20),
            "price_vs_sma_50": self._calculate_price_vs_sma(current_price, sma_50),
            "price_vs_sma_200": self._calculate_price_vs_sma(current_price, sma_200),
        }

    def get_volatility_metrics(
        self, ticker: str, period: str = "1y", session: Session | None = None
    ) -> VolatilityMetricsDict:
        """Retrieve volatility metrics for a given ticker.

        Args:
            ticker: Stock ticker symbol.
            period: Historical data period (default: "1y").
            session: Optional curl_cffi session for requests.

        Returns:
            Dictionary containing volatility metrics including daily and
            annualized volatility, max gains/losses, and trading day stats.

        Raises:
            ValueError: If no historical data is available for the ticker.
        """
        stock = yf.Ticker(ticker, session=session)
        hist = stock.history(period=period)

        if hist.empty:
            raise ValueError("No historical data available")

        daily_returns = hist["Close"].pct_change().dropna()
        daily_volatility = daily_returns.std()
        annualized_volatility = self._calculate_annualized_volatility(daily_volatility)

        max_daily_gain = daily_returns.max()
        max_daily_loss = daily_returns.min()

        positive_days = int((daily_returns > 0).sum())
        negative_days = int((daily_returns < 0).sum())
        total_days = len(daily_returns)

        return self._build_volatility_dict(
            daily_volatility=daily_volatility,
            annualized_volatility=annualized_volatility,
            max_daily_gain=max_daily_gain,
            max_daily_loss=max_daily_loss,
            positive_days=positive_days,
            negative_days=negative_days,
            total_days=total_days,
        )

    def _calculate_annualized_volatility(self, daily_volatility: float) -> float:
        """Calculate annualized volatility from daily volatility.

        Args:
            daily_volatility: Daily volatility standard deviation.

        Returns:
            Annualized volatility (assumes 252 trading days per year).
        """
        return daily_volatility * (252**0.5)

    def _calculate_positive_days_percentage(self, positive_days: int, total_days: int) -> float:
        """Calculate percentage of positive trading days.

        Args:
            positive_days: Number of days with positive returns.
            total_days: Total number of trading days.

        Returns:
            Percentage of positive days or 0.0 if no trading days.
        """
        if total_days == 0:
            return 0.0
        return (positive_days / total_days) * 100

    def _build_volatility_dict(
        self,
        daily_volatility: float,
        annualized_volatility: float,
        max_daily_gain: float,
        max_daily_loss: float,
        positive_days: int,
        negative_days: int,
        total_days: int,
    ) -> VolatilityMetricsDict:
        """Build volatility metrics dictionary.

        Args:
            daily_volatility: Daily volatility standard deviation.
            annualized_volatility: Annualized volatility.
            max_daily_gain: Maximum daily percentage gain.
            max_daily_loss: Maximum daily percentage loss.
            positive_days: Number of positive trading days.
            negative_days: Number of negative trading days.
            total_days: Total number of trading days.

        Returns:
            Dictionary containing all volatility metrics.
        """
        return {
            "daily_volatility": float(daily_volatility),
            "annualized_volatility": float(annualized_volatility),
            "max_daily_gain_percent": float(max_daily_gain) * 100,
            "max_daily_loss_percent": float(max_daily_loss) * 100,
            "positive_days": positive_days,
            "negative_days": negative_days,
            "total_trading_days": total_days,
            "positive_days_percentage": self._calculate_positive_days_percentage(positive_days, total_days),
        }

    def get_support_resistance_levels(
        self, ticker: str, period: str = "6mo", session: Session | None = None
    ) -> SupportResistanceLevelsDict:
        """Retrieve support and resistance levels for a given ticker.

        Args:
            ticker: Stock ticker symbol.
            period: Historical data period (default: "6mo").
            session: Optional curl_cffi session for requests.

        Returns:
            Dictionary containing support and resistance levels based on
            historical highs and lows relative to current price.

        Raises:
            ValueError: If no historical data is available for the ticker.
        """
        stock = yf.Ticker(ticker, session=session)
        hist = stock.history(period=period)

        if hist.empty:
            raise ValueError("No historical data available")

        current_price = float(hist["Close"].iloc[-1])
        highs = hist["High"]
        lows = hist["Low"]

        resistance_levels = self._extract_resistance_levels(highs, current_price)
        support_levels = self._extract_support_levels(lows, current_price)

        return self._build_levels_dict(
            current_price=current_price,
            resistance_levels=resistance_levels,
            support_levels=support_levels,
        )

    def _extract_resistance_levels(self, highs, current_price: float) -> list[float]:
        """Extract resistance levels from historical highs.

        Args:
            highs: Historical high prices series.
            current_price: Current stock price.

        Returns:
            List of top 5 resistance levels above current price.
        """
        top_highs = highs.nlargest(10).unique()
        resistance_levels = [float(high) for high in top_highs if high > current_price]
        return sorted(resistance_levels)[:5]

    def _extract_support_levels(self, lows, current_price: float) -> list[float]:
        """Extract support levels from historical lows.

        Args:
            lows: Historical low prices series.
            current_price: Current stock price.

        Returns:
            List of top 5 support levels below current price.
        """
        bottom_lows = lows.nsmallest(10).unique()
        support_levels = [float(low) for low in bottom_lows if low < current_price]
        return sorted(support_levels, reverse=True)[:5]

    def _get_nearest_resistance(self, resistance_levels: list[float]) -> float | None:
        """Get nearest resistance level.

        Args:
            resistance_levels: List of resistance levels.

        Returns:
            Nearest resistance level or None if no levels exist.
        """
        if not resistance_levels:
            return None
        return resistance_levels[0]

    def _get_nearest_support(self, support_levels: list[float]) -> float | None:
        """Get nearest support level.

        Args:
            support_levels: List of support levels.

        Returns:
            Nearest support level or None if no levels exist.
        """
        if not support_levels:
            return None
        return support_levels[0]

    def _build_levels_dict(
        self,
        current_price: float,
        resistance_levels: list[float],
        support_levels: list[float],
    ) -> SupportResistanceLevelsDict:
        """Build support and resistance levels dictionary.

        Args:
            current_price: Current stock price.
            resistance_levels: List of resistance levels.
            support_levels: List of support levels.

        Returns:
            Dictionary containing all support and resistance data.
        """
        return {
            "current_price": current_price,
            "resistance_levels": resistance_levels,
            "support_levels": support_levels,
            "nearest_resistance": self._get_nearest_resistance(resistance_levels),
            "nearest_support": self._get_nearest_support(support_levels),
        }
