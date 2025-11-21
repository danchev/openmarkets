from abc import ABC, abstractmethod

import yfinance as yf

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
    def fetch_analyst_recommendations(self, ticker: str) -> list[AnalystRecommendation]:
        pass

    @abstractmethod
    def fetch_recommendation_changes(self, ticker: str) -> list[AnalystRecommendationChange]:
        pass

    @abstractmethod
    def fetch_revenue_estimates(self, ticker: str) -> list[RevenueEstimate]:
        pass

    @abstractmethod
    def fetch_earnings_estimates(self, ticker: str) -> list[EarningsEstimate]:
        pass

    @abstractmethod
    def fetch_growth_estimates(self, ticker: str) -> list[GrowthEstimates]:
        pass

    @abstractmethod
    def fetch_eps_trends(self, ticker: str) -> list[EPSTrend]:
        pass

    @abstractmethod
    def fetch_price_targets(self, ticker: str) -> AnalystPriceTargets:
        pass


class YFinanceAnalysisRepository(IAnalysisRepository):
    """YFinance implementation of IAnalysisRepository."""

    def fetch_analyst_recommendations(self, ticker: str) -> list[AnalystRecommendation]:
        yf_ticker = yf.Ticker(ticker)
        data = getattr(yf_ticker, "recommendations_summary", None)
        if data is None or getattr(data, "empty", True):
            return []
        # Assume DataFrame with columns matching AnalystRecommendation
        return [AnalystRecommendation(**rec) for rec in data.to_dict("records")]

    def fetch_recommendation_changes(self, ticker: str) -> list[AnalystRecommendationChange]:
        yf_ticker = yf.Ticker(ticker)
        data = getattr(yf_ticker, "upgrades_downgrades", None)
        if data is None or getattr(data, "empty", True):
            return []
        return [AnalystRecommendationChange(**rec) for rec in data.to_dict("records")]

    def fetch_revenue_estimates(self, ticker: str) -> list[RevenueEstimate]:
        yf_ticker = yf.Ticker(ticker)
        data = getattr(yf_ticker, "revenue_estimate", None)
        if data is None or getattr(data, "empty", True):
            return []
        return [RevenueEstimate(**rec) for rec in data.to_dict("records")]

    def fetch_earnings_estimates(self, ticker: str) -> list[EarningsEstimate]:
        yf_ticker = yf.Ticker(ticker)
        data = getattr(yf_ticker, "earnings_estimate", None)
        if data is None or getattr(data, "empty", True):
            return []
        return [EarningsEstimate(**rec) for rec in data.to_dict("records")]

    def fetch_growth_estimates(self, ticker: str) -> list[GrowthEstimates]:
        yf_ticker = yf.Ticker(ticker)
        data = getattr(yf_ticker, "growth_estimates", None)
        if data is None or getattr(data, "empty", True):
            return []
        return [GrowthEstimates(**rec) for rec in data.to_dict("records")]

    def fetch_eps_trends(self, ticker: str) -> list[EPSTrend]:
        yf_ticker = yf.Ticker(ticker)
        data = getattr(yf_ticker, "eps_trend", None)
        if data is None or getattr(data, "empty", True):
            return []
        return [EPSTrend(**rec) for rec in data.to_dict("records")]

    def fetch_price_targets(self, ticker: str) -> AnalystPriceTargets:
        yf_ticker = yf.Ticker(ticker)
        data = getattr(yf_ticker, "analyst_price_target", None)
        if not data or not isinstance(data, dict):
            # Provide default values for all required fields
            return AnalystPriceTargets(current=None, high=None, low=None, mean=None, median=None)
        return AnalystPriceTargets(**data)
