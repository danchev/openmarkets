"""Tests for AnalysisService.

Verifies that the service layer correctly delegates to the repository
for all analysis-related methods.
"""

from unittest.mock import MagicMock, patch

import pytest

from openmarkets.repositories.analysis import IAnalysisRepository
from openmarkets.schemas.analysis import (
    AnalystPriceTargets,
    AnalystRecommendation,
    AnalystRecommendationChange,
    EarningsEstimate,
    EPSTrend,
    GrowthEstimates,
    RevenueEstimate,
)
from openmarkets.services.analysis import AnalysisService


class AnalysisRepositorySpy(IAnalysisRepository):
    """Spy implementation of IAnalysisRepository for testing."""

    def __init__(self):
        self.calls = {}

    def _record(self, method_name, *args, **kwargs):
        """Record a method call."""
        self.calls[method_name] = self.calls.get(method_name, 0) + 1

    def get_analyst_recommendations(self, ticker, session=None):
        self._record("get_analyst_recommendations", ticker)
        return [
            AnalystRecommendation(
                **{
                    "period": "0m",
                    "strongBuy": 5,
                    "buy": 10,
                    "hold": 3,
                    "sell": 1,
                    "strongSell": 0,
                }
            )
        ]

    def get_recommendation_changes(self, ticker, session=None):
        self._record("get_recommendation_changes", ticker)
        return [
            AnalystRecommendationChange(
                **{
                    "Date": "2024-01-15",
                    "Firm": "Morgan Stanley",
                    "To Rating": "Buy",
                    "From Rating": "Hold",
                    "Action": "upgrade",
                    "Notes": None,
                }
            )
        ]

    def get_revenue_estimates(self, ticker, session=None):
        self._record("get_revenue_estimates", ticker)
        return [
            RevenueEstimate(
                **{
                    "period": "0q",
                    "avg": 1000000,
                    "low": 900000,
                    "high": 1100000,
                    "numberOfAnalysts": 10,
                    "yearAgoRevenue": 900000,
                    "growth": 0.11,
                }
            )
        ]

    def get_earnings_estimates(self, ticker, session=None):
        self._record("get_earnings_estimates", ticker)
        return [
            EarningsEstimate(
                **{
                    "period": "0q",
                    "avg": 2.5,
                    "low": 2.0,
                    "high": 3.0,
                    "numberOfAnalysts": 12,
                    "yearAgoEps": 2.2,
                    "growth": 0.14,
                }
            )
        ]

    def get_growth_estimates(self, ticker, session=None):
        self._record("get_growth_estimates", ticker)
        return [
            GrowthEstimates(
                **{
                    "period": "Next 5 Years",
                    "stockTrend": 0.15,
                    "indexTrend": 0.10,
                }
            )
        ]

    def get_eps_trends(self, ticker, session=None):
        self._record("get_eps_trends", ticker)
        return [
            EPSTrend(
                **{
                    "period": "0q",
                    "current": 2.5,
                    "7daysAgo": 2.4,
                    "30daysAgo": 2.3,
                    "60daysAgo": 2.2,
                    "90daysAgo": 2.1,
                }
            )
        ]

    def get_price_targets(self, ticker, session=None):
        self._record("get_price_targets", ticker)
        return AnalystPriceTargets(
            **{
                "current": 150.0,
                "high": 200.0,
                "low": 120.0,
                "mean": 165.0,
                "median": 160.0,
            }
        )


@pytest.fixture
def spy_repository():
    """Create a spy repository for testing service delegation."""
    return AnalysisRepositorySpy()


@pytest.fixture
def service(spy_repository):
    """Create AnalysisService with spy repository."""
    return AnalysisService(repository=spy_repository)


class TestAnalysisServiceDelegatesToRepository:
    """Test that all service methods delegate to the repository."""

    def test_get_analyst_recommendations(self, service, spy_repository):
        """Test that get_analyst_recommendations delegates to repository."""
        result = service.get_analyst_recommendations("AAPL")
        assert len(result) == 1
        assert result[0].strong_buy == 5
        assert spy_repository.calls["get_analyst_recommendations"] == 1

    def test_get_recommendation_changes(self, service, spy_repository):
        """Test that get_recommendation_changes delegates to repository."""
        result = service.get_recommendation_changes("AAPL")
        assert len(result) == 1
        assert result[0].firm == "Morgan Stanley"
        assert spy_repository.calls["get_recommendation_changes"] == 1

    def test_get_revenue_estimates(self, service, spy_repository):
        """Test that get_revenue_estimates delegates to repository."""
        result = service.get_revenue_estimates("AAPL")
        assert len(result) == 1
        assert result[0].avg == 1000000
        assert spy_repository.calls["get_revenue_estimates"] == 1

    def test_get_earnings_estimates(self, service, spy_repository):
        """Test that get_earnings_estimates delegates to repository."""
        result = service.get_earnings_estimates("AAPL")
        assert len(result) == 1
        assert result[0].avg == 2.5
        assert spy_repository.calls["get_earnings_estimates"] == 1

    def test_get_growth_estimates(self, service, spy_repository):
        """Test that get_growth_estimates delegates to repository."""
        result = service.get_growth_estimates("AAPL")
        assert len(result) == 1
        assert result[0].stock_trend == 0.15
        assert spy_repository.calls["get_growth_estimates"] == 1

    def test_get_eps_trends(self, service, spy_repository):
        """Test that get_eps_trends delegates to repository."""
        result = service.get_eps_trends("AAPL")
        assert len(result) == 1
        assert result[0].current == 2.5
        assert spy_repository.calls["get_eps_trends"] == 1

    def test_get_price_targets(self, service, spy_repository):
        """Test that get_price_targets delegates to repository."""
        result = service.get_price_targets("AAPL")
        assert result.current == 150.0
        assert result.high == 200.0
        assert result.low == 120.0
        assert result.mean == 165.0
        assert result.median == 160.0
        assert spy_repository.calls["get_price_targets"] == 1

    def test_get_full_analysis(self, service, spy_repository):
        """Test that get_full_analysis aggregates all analysis data."""
        result = service.get_full_analysis("AAPL")
        assert "recommendations" in result
        assert "recommendation_changes" in result
        assert "revenue_estimates" in result
        assert "earnings_estimates" in result
        assert "growth_estimates" in result
        assert "eps_trends" in result
        assert "price_targets" in result
        assert len(result["recommendations"]) == 1
        assert len(result["recommendation_changes"]) == 1
        assert len(result["revenue_estimates"]) == 1
        assert len(result["earnings_estimates"]) == 1
        assert len(result["growth_estimates"]) == 1
        assert len(result["eps_trends"]) == 1
        assert result["price_targets"].current == 150.0

        # Verify all methods were called
        expected_calls = [
            "get_analyst_recommendations",
            "get_recommendation_changes",
            "get_revenue_estimates",
            "get_earnings_estimates",
            "get_growth_estimates",
            "get_eps_trends",
            "get_price_targets",
        ]
        for call in expected_calls:
            assert spy_repository.calls.get(call) == 1, f"Expected {call} to be called once"
