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
    """Repository interface for analysis data access."""

    @abstractmethod
    def get_analyst_recommendations(self, ticker: str, session: Session | None = None) -> list[AnalystRecommendation]:
        pass

    @abstractmethod
    def get_recommendation_changes(
        self, ticker: str, session: Session | None = None
    ) -> list[AnalystRecommendationChange]:
        pass

    @abstractmethod
    def get_revenue_estimates(self, ticker: str, session: Session | None = None) -> list[RevenueEstimate]:
        pass

    @abstractmethod
    def get_earnings_estimates(self, ticker: str, session: Session | None = None) -> list[EarningsEstimate]:
        pass

    @abstractmethod
    def get_growth_estimates(self, ticker: str, session: Session | None = None) -> list[GrowthEstimates]:
        pass

    @abstractmethod
    def get_eps_trends(self, ticker: str, session: Session | None = None) -> list[EPSTrend]:
        pass

    @abstractmethod
    def get_price_targets(self, ticker: str, session: Session | None = None) -> AnalystPriceTargets:
        pass


class YFinanceAnalysisRepository(IAnalysisRepository):
    """YFinance implementation of IAnalysisRepository."""

    def get_analyst_recommendations(self, ticker: str, session: Session | None = None) -> list[AnalystRecommendation]:
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "recommendations_summary", None)
        if data is None or getattr(data, "empty", True):
            return []
        # Assume DataFrame with columns matching AnalystRecommendation
        return [AnalystRecommendation(**rec) for rec in data.to_dict("records")]

    def get_recommendation_changes(
        self, ticker: str, session: Session | None = None
    ) -> list[AnalystRecommendationChange]:
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "upgrades_downgrades", None)
        if data is None or getattr(data, "empty", True):
            return []
        return [AnalystRecommendationChange(**rec) for rec in data.to_dict("records")]

    def get_revenue_estimates(self, ticker: str, session: Session | None = None) -> list[RevenueEstimate]:
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "revenue_estimate", None)
        if data is None or getattr(data, "empty", True):
            return []
        return [RevenueEstimate(**rec) for rec in data.to_dict("records")]

    def get_earnings_estimates(self, ticker: str, session: Session | None = None) -> list[EarningsEstimate]:
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "earnings_estimate", None)
        if data is None or getattr(data, "empty", True):
            return []
        return [EarningsEstimate(**rec) for rec in data.to_dict("records")]

    def get_growth_estimates(self, ticker: str, session: Session | None = None) -> list[GrowthEstimates]:
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "growth_estimates", None)
        if data is None or getattr(data, "empty", True):
            return []
        return [GrowthEstimates(**rec) for rec in data.to_dict("records")]

    def get_eps_trends(self, ticker: str, session: Session | None = None) -> list[EPSTrend]:
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "eps_trend", None)
        if data is None or getattr(data, "empty", True):
            return []
        return [EPSTrend(**rec) for rec in data.to_dict("records")]

    def get_price_targets(self, ticker: str, session: Session | None = None) -> AnalystPriceTargets:
        yf_ticker = yf.Ticker(ticker, session=session)
        data = getattr(yf_ticker, "analyst_price_target", None)
        if not data or not isinstance(data, dict):
            # Provide default values for all required fields
            return AnalystPriceTargets(current=None, high=None, low=None, mean=None, median=None)
        return AnalystPriceTargets(**data)
