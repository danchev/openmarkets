from abc import ABC, abstractmethod

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.schemas.technical_analysis import (
    SupportResistanceLevelsDict,
    TechnicalIndicatorsDict,
    VolatilityMetricsDict,
)


class ITechnicalAnalysisRepository(ABC):
    @abstractmethod
    def get_technical_indicators(
        self, ticker: str, period: str = "6mo", session: Session | None = None
    ) -> TechnicalIndicatorsDict:
        pass

    @abstractmethod
    def get_volatility_metrics(
        self, ticker: str, period: str = "1y", session: Session | None = None
    ) -> VolatilityMetricsDict:
        pass

    @abstractmethod
    def get_support_resistance_levels(
        self, ticker: str, period: str = "6mo", session: Session | None = None
    ) -> SupportResistanceLevelsDict:
        pass


class YFinanceTechnicalAnalysisRepository(ITechnicalAnalysisRepository):
    def get_technical_indicators(
        self, ticker: str, period: str = "6mo", session: Session | None = None
    ) -> TechnicalIndicatorsDict:
        stock = yf.Ticker(ticker, session=session)
        hist = stock.history(period=period)
        if hist.empty:
            raise ValueError("No historical data available")
        current_price = hist["Close"].iloc[-1]
        high_52w = hist["High"].max()
        low_52w = hist["Low"].min()
        avg_volume = hist["Volume"].mean()
        sma_20 = hist["Close"].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else None
        sma_50 = hist["Close"].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else None
        sma_200 = hist["Close"].rolling(window=200).mean().iloc[-1] if len(hist) >= 200 else None
        price_position = ((current_price - low_52w) / (high_52w - low_52w)) * 100 if (high_52w - low_52w) != 0 else None
        indicators: TechnicalIndicatorsDict = {
            "current_price": float(current_price),
            "fifty_two_week_high": float(high_52w),
            "fifty_two_week_low": float(low_52w),
            "price_position_in_52w_range_percent": float(price_position) if price_position is not None else None,
            "average_volume": float(avg_volume),
            "sma_20": float(sma_20) if sma_20 is not None else None,
            "sma_50": float(sma_50) if sma_50 is not None else None,
            "sma_200": float(sma_200) if sma_200 is not None else None,
            "price_vs_sma_20": ((float(current_price) - float(sma_20)) / float(sma_20) * 100)
            if sma_20 is not None and sma_20 != 0
            else None,
            "price_vs_sma_50": ((float(current_price) - float(sma_50)) / float(sma_50) * 100)
            if sma_50 is not None and sma_50 != 0
            else None,
            "price_vs_sma_200": ((float(current_price) - float(sma_200)) / float(sma_200) * 100)
            if sma_200 is not None and sma_200 != 0
            else None,
        }
        return indicators

    def get_volatility_metrics(
        self, ticker: str, period: str = "1y", session: Session | None = None
    ) -> VolatilityMetricsDict:
        stock = yf.Ticker(ticker, session=session)
        hist = stock.history(period=period)
        if hist.empty:
            raise ValueError("No historical data available")
        daily_returns = hist["Close"].pct_change().dropna()
        daily_volatility = daily_returns.std()
        annualized_volatility = daily_volatility * (252**0.5)
        max_daily_gain = daily_returns.max()
        max_daily_loss = daily_returns.min()
        positive_days = int((daily_returns > 0).sum())
        negative_days = int((daily_returns < 0).sum())
        total_days = len(daily_returns)
        volatility_data: VolatilityMetricsDict = {
            "daily_volatility": float(daily_volatility),
            "annualized_volatility": float(annualized_volatility),
            "max_daily_gain_percent": float(max_daily_gain) * 100,
            "max_daily_loss_percent": float(max_daily_loss) * 100,
            "positive_days": positive_days,
            "negative_days": negative_days,
            "total_trading_days": total_days,
            "positive_days_percentage": (positive_days / total_days * 100) if total_days > 0 else 0.0,
        }
        return volatility_data

    def get_support_resistance_levels(
        self, ticker: str, period: str = "6mo", session: Session | None = None
    ) -> SupportResistanceLevelsDict:
        stock = yf.Ticker(ticker, session=session)
        hist = stock.history(period=period)
        if hist.empty:
            raise ValueError("No historical data available")
        highs = hist["High"]
        lows = hist["Low"]
        current_price = float(hist["Close"].iloc[-1])
        resistance_levels = []
        support_levels = []
        top_highs = highs.nlargest(10).unique()
        for high in top_highs:
            if high > current_price:
                resistance_levels.append(float(high))
        bottom_lows = lows.nsmallest(10).unique()
        for low in bottom_lows:
            if low < current_price:
                support_levels.append(float(low))
        resistance_levels = sorted(resistance_levels)[:5]
        support_levels = sorted(support_levels, reverse=True)[:5]
        levels_data: SupportResistanceLevelsDict = {
            "current_price": current_price,
            "resistance_levels": resistance_levels,
            "support_levels": support_levels,
            "nearest_resistance": resistance_levels[0] if resistance_levels else None,
            "nearest_support": support_levels[0] if support_levels else None,
        }
        return levels_data
