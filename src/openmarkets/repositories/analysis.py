"""Repository layer for stock analysis data operations.

Provides abstractions and implementations for fetching analyst recommendations,
earnings estimates, revenue estimates, and other analysis-related data.
"""

from abc import ABC, abstractmethod

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.schemas.analysis import (
    AnalystPriceTargets,
    AnalystRecommendation,
    AnalystRecommendationChange,
    EarningsEstimate,
    EPSTrend,
    GrowthEstimates,
    RevenueEstimate,
)


class IAnalysisRepository(ABC):
    """Abstract interface for stock analysis data repositories."""

    @abstractmethod
    def get_analyst_recommendations(self, ticker: str, session: Session | None = None) -> list[AnalystRecommendation]:
        """Retrieve analyst recommendations for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of analyst recommendations.
        """
        pass

    @abstractmethod
    def get_recommendation_changes(
        self, ticker: str, session: Session | None = None
    ) -> list[AnalystRecommendationChange]:
        """Retrieve recommendation changes for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of recommendation changes.
        """
        pass

    @abstractmethod
    def get_revenue_estimates(self, ticker: str, session: Session | None = None) -> list[RevenueEstimate]:
        """Retrieve revenue estimates for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of revenue estimates.
        """
        pass

    @abstractmethod
    def get_earnings_estimates(self, ticker: str, session: Session | None = None) -> list[EarningsEstimate]:
        """Retrieve earnings estimates for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of earnings estimates.
        """
        pass

    @abstractmethod
    def get_growth_estimates(self, ticker: str, session: Session | None = None) -> list[GrowthEstimates]:
        """Retrieve growth estimates for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of growth estimates.
        """
        pass

    @abstractmethod
    def get_eps_trends(self, ticker: str, session: Session | None = None) -> list[EPSTrend]:
        """Retrieve EPS trends for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of EPS trends.
        """
        pass

    @abstractmethod
    def get_price_targets(self, ticker: str, session: Session | None = None) -> AnalystPriceTargets:
        """Retrieve analyst price targets for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Analyst price targets.
        """
        pass


class YFinanceAnalysisRepository(IAnalysisRepository):
    """YFinance implementation of IAnalysisRepository."""

    def get_analyst_recommendations(self, ticker: str, session: Session | None = None) -> list[AnalystRecommendation]:
        """Retrieve analyst recommendations for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of analyst recommendations.
        """
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "recommendations_summary", None)
        if data is None:
            return []
        if getattr(data, "empty", True):
            return []
        records = data.to_dict("records")
        return [AnalystRecommendation(**rec) for rec in records]

    def get_recommendation_changes(
        self, ticker: str, session: Session | None = None
    ) -> list[AnalystRecommendationChange]:
        """Retrieve recommendation changes for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of recommendation changes.
        """
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "upgrades_downgrades", None)
        if data is None:
            return []
        if getattr(data, "empty", True):
            return []
        records = data.to_dict("records")
        return [AnalystRecommendationChange(**rec) for rec in records]

    def get_revenue_estimates(self, ticker: str, session: Session | None = None) -> list[RevenueEstimate]:
        """Retrieve revenue estimates for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of revenue estimates.
        """
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "revenue_estimate", None)
        if data is None:
            return []
        if getattr(data, "empty", True):
            return []
        records = data.to_dict("records")
        return [RevenueEstimate(**rec) for rec in records]

    def get_earnings_estimates(self, ticker: str, session: Session | None = None) -> list[EarningsEstimate]:
        """Retrieve earnings estimates for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of earnings estimates.
        """
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "earnings_estimate", None)
        if data is None:
            return []
        if getattr(data, "empty", True):
            return []
        records = data.to_dict("records")
        return [EarningsEstimate(**rec) for rec in records]

    def get_growth_estimates(self, ticker: str, session: Session | None = None) -> list[GrowthEstimates]:
        """Retrieve growth estimates for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of growth estimates.
        """
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "growth_estimates", None)
        if data is None:
            return []
        if getattr(data, "empty", True):
            return []
        records = data.to_dict("records")
        return [GrowthEstimates(**rec) for rec in records]

    def get_eps_trends(self, ticker: str, session: Session | None = None) -> list[EPSTrend]:
        """Retrieve EPS trends for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of EPS trends.
        """
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "eps_trend", None)
        if data is None:
            return []
        if getattr(data, "empty", True):
            return []
        records = data.to_dict("records")
        return [EPSTrend(**rec) for rec in records]

    def get_price_targets(self, ticker: str, session: Session | None = None) -> AnalystPriceTargets:
        """Retrieve analyst price targets for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Analyst price targets.
        """
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "analyst_price_target", None)
        if not data:
            return AnalystPriceTargets(current=None, high=None, low=None, mean=None, median=None)
        if not isinstance(data, dict):
            return AnalystPriceTargets(current=None, high=None, low=None, mean=None, median=None)
        return AnalystPriceTargets(**data)
