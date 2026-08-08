"""Real Yahoo Finance API tests for ScreenerService (yfinance 1.3.0)."""

import pytest

from openmarkets.schemas.screener import ScreenerResult
from openmarkets.services.screener import ScreenerService
from tests.live.conftest import tolerate_network_errors


def test_screen_day_gainers_against_real_api():
    with tolerate_network_errors("screen"):
        result = ScreenerService().search_screener_matches("day_gainers", count=5)

    assert isinstance(result, ScreenerResult)
    assert result.total > 0
    assert result.quotes
    assert all(quote.symbol for quote in result.quotes)


def test_screen_top_etfs_market_cap_is_none_against_real_api():
    """ETF quotes report net_assets instead of market_cap upstream."""
    with tolerate_network_errors("screen"):
        result = ScreenerService().search_screener_matches("top_etfs_us", count=5)

    assert result.quotes
    assert all(quote.market_cap is None for quote in result.quotes)


def test_screen_rejects_unknown_query_without_network_call():
    with pytest.raises(ValueError, match="Unknown predefined screen"):
        ScreenerService().search_screener_matches("not_a_real_screen")  # type: ignore[arg-type]


def test_screen_forwards_count_against_real_api():
    """yfinance's screen() does not clamp results to count client-side for
    every named screen (confirmed: 'most_actives' returns its own fixed page
    size regardless of a smaller count), so this only proves the parameter
    reaches the request without erroring - not that it is a hard cap."""
    with tolerate_network_errors("screen"):
        result = ScreenerService().search_screener_matches("most_actives", count=3)

    assert result.quotes
