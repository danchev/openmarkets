"""Real Yahoo Finance API tests for TechnicalAnalysisService.

This service had zero coverage at the service layer before this file - the
existing test_services_technical_analysis.py file (despite its name) only
ever calls YFinanceTechnicalAnalysisRepository directly, never the service.
"""

from openmarkets.services.technical_analysis import TechnicalAnalysisService
from tests.live.conftest import STABLE_TICKER


def test_get_technical_indicators_against_real_api():
    result = TechnicalAnalysisService().get_technical_indicators(STABLE_TICKER)

    assert result["current_price"] > 0
    assert result["fifty_two_week_high"] >= result["fifty_two_week_low"]


def test_get_volatility_metrics_against_real_api():
    result = TechnicalAnalysisService().get_volatility_metrics(STABLE_TICKER)

    assert result["annualized_volatility"] >= 0
    assert 0 <= result["positive_days_percentage"] <= 100


def test_get_support_resistance_levels_against_real_api():
    result = TechnicalAnalysisService().get_support_resistance_levels(STABLE_TICKER)

    assert result["current_price"] > 0
    assert isinstance(result["resistance_levels"], list)
    assert isinstance(result["support_levels"], list)
