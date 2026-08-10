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


def test_get_global_indices_live():
    from openmarkets.schemas.markets import GlobalMarketSnapshot
    from tests.live.conftest import tolerate_network_errors

    with tolerate_network_errors("WSJ Global Indices"):
        svc = MarketsService()
        snapshot = svc.get_global_indices()

        assert isinstance(snapshot, GlobalMarketSnapshot)
        assert len(snapshot.indices) > 5
        assert all(idx.value > 0 for idx in snapshot.indices)
        spx = next((idx for idx in snapshot.indices if idx.symbol == "SP500"), None)
        assert spx is not None


def test_get_volatility_vix_live():
    from openmarkets.schemas.markets import GlobalIndexQuote
    from tests.live.conftest import tolerate_network_errors

    with tolerate_network_errors("WSJ VIX"):
        svc = MarketsService()
        vix = svc.get_volatility_vix()

        assert isinstance(vix, GlobalIndexQuote)
        assert vix.symbol == "VIX"
        assert vix.value > 0
