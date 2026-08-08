"""Real Yahoo Finance API tests for AnalysisService.

This service had zero coverage at the service layer before this file.
"""

from openmarkets.schemas.analysis import (
    AnalystPriceTargets,
    AnalystRecommendation,
    AnalystRecommendationChange,
    EarningsEstimate,
    EPSTrend,
    FullAnalysis,
    GrowthEstimates,
    RevenueEstimate,
)
from openmarkets.services.analysis import AnalysisService
from tests.live.conftest import STABLE_TICKER


def test_get_analyst_recommendations_against_real_api():
    result = AnalysisService().get_analyst_recommendations(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, AnalystRecommendation) for entry in result)


def test_get_recommendation_changes_against_real_api():
    result = AnalysisService().get_recommendation_changes(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, AnalystRecommendationChange) for entry in result)


def test_get_revenue_estimates_against_real_api():
    result = AnalysisService().get_revenue_estimates(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, RevenueEstimate) for entry in result)


def test_get_earnings_estimates_against_real_api():
    result = AnalysisService().get_earnings_estimates(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, EarningsEstimate) for entry in result)


def test_get_growth_estimates_against_real_api():
    result = AnalysisService().get_growth_estimates(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, GrowthEstimates) for entry in result)


def test_get_eps_trends_against_real_api():
    result = AnalysisService().get_eps_trends(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, EPSTrend) for entry in result)


def test_get_price_targets_against_real_api():
    result = AnalysisService().get_price_targets(STABLE_TICKER)

    assert isinstance(result, AnalystPriceTargets)


def test_get_full_analysis_against_real_api():
    """Exercises the concurrent gather() fan-out from an earlier session
    against real, independently-latent upstream endpoints."""
    result = AnalysisService().get_full_analysis(STABLE_TICKER)

    assert isinstance(result, FullAnalysis)
    assert isinstance(result.recommendations, list)
    assert isinstance(result.price_targets, AnalystPriceTargets)
