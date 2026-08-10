"""Unit tests for MarketsService."""

from unittest.mock import Mock

from openmarkets.schemas.markets import GlobalIndexQuote, GlobalMarketSnapshot, MarketStatus, MarketSummary
from openmarkets.services.markets import MarketsService


def test_markets_service_delegation():
    yf_mock = Mock()
    wsj_mock = Mock()

    mock_summary = MarketSummary(summary={})
    mock_status = MarketStatus(id="us_market", name="US", status="OPEN")
    mock_global = GlobalMarketSnapshot(as_of="2026-08-09", indices=[])
    mock_vix = GlobalIndexQuote(symbol="VIX", name="CBOE Volatility Index", region="US", value=15.0, date="2026-08-09")

    yf_mock.get_market_summary.return_value = mock_summary
    yf_mock.get_market_status.return_value = mock_status
    wsj_mock.get_global_indices.return_value = mock_global
    wsj_mock.get_volatility_vix.return_value = mock_vix

    svc = MarketsService(repository=yf_mock, wsj_repository=wsj_mock)

    assert svc.get_market_summary("US") == mock_summary
    yf_mock.get_market_summary.assert_called_with(market="US", session=svc.session)

    assert svc.get_market_status("US") == mock_status
    yf_mock.get_market_status.assert_called_with(market="US", session=svc.session)

    assert svc.get_global_indices() == mock_global
    wsj_mock.get_global_indices.assert_called_with(session=svc.session)

    assert svc.get_volatility_vix() == mock_vix
    wsj_mock.get_volatility_vix.assert_called_with(session=svc.session)
