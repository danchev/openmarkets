"""Real Yahoo Finance API tests for MarketsService.

This service had zero coverage at the service layer before this file.
"""

from openmarkets.schemas.markets import MarketStatus, MarketSummary
from openmarkets.services.markets import MarketsService
from tests.live.conftest import STABLE_MARKET


def test_get_market_summary_against_real_api():
    result = MarketsService().get_market_summary(STABLE_MARKET)

    assert isinstance(result, MarketSummary)


def test_get_market_status_against_real_api():
    result = MarketsService().get_market_status(STABLE_MARKET)

    assert isinstance(result, MarketStatus)
