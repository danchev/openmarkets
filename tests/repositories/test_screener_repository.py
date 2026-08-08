"""Unit tests for YFinanceScreenerRepository."""

import pytest

from openmarkets.repositories.screener import YFinanceScreenerRepository
from openmarkets.schemas.screener import ScreenerResult


@pytest.fixture
def screener_repository() -> YFinanceScreenerRepository:
    return YFinanceScreenerRepository()


def test_screen_returns_parsed_result(screener_repository, monkeypatch):
    fake_response = {
        "total": 42,
        "quotes": [
            {"symbol": "AAA", "quoteType": "EQUITY", "shortName": "Alpha Co", "regularMarketPrice": 10.0},
            {"symbol": "BBB", "quoteType": "ETF", "netAssets": 5_000_000.0},
        ],
    }

    def fake_screen(query, count=None, offset=None, session=None):
        return fake_response

    monkeypatch.setattr("openmarkets.repositories.screener.yf.screen", fake_screen)

    result = screener_repository.screen("day_gainers")

    assert isinstance(result, ScreenerResult)
    assert result.total == 42
    assert len(result.quotes) == 2
    assert result.quotes[0].symbol == "AAA"
    assert result.quotes[0].quote_type == "EQUITY"
    assert result.quotes[1].net_assets == 5_000_000.0
    # market_cap is absent for the ETF quote - must default to None, not error
    assert result.quotes[1].market_cap is None


def test_screen_normalizes_nan_metrics_to_none(screener_repository, monkeypatch):
    """A screener quote can carry the same float-NaN-for-missing-value
    pattern seen elsewhere in this project (valuation, sector/industry
    listings)."""
    fake_response = {
        "total": 1,
        "quotes": [{"symbol": "AAA", "marketCap": float("nan"), "fiftyTwoWeekHigh": float("nan")}],
    }
    monkeypatch.setattr(
        "openmarkets.repositories.screener.yf.screen",
        lambda query, count=None, offset=None, session=None: fake_response,
    )

    result = screener_repository.screen("day_gainers")

    assert result.quotes[0].market_cap is None
    assert result.quotes[0].fifty_two_week_high is None


def test_screen_forwards_count_and_offset(screener_repository, monkeypatch):
    captured = {}

    def fake_screen(query, count=None, offset=None, session=None):
        captured["query"] = query
        captured["count"] = count
        captured["offset"] = offset
        return {"total": 0, "quotes": []}

    monkeypatch.setattr("openmarkets.repositories.screener.yf.screen", fake_screen)

    screener_repository.screen("most_actives", count=10, offset=20)

    assert captured == {"query": "most_actives", "count": 10, "offset": 20}


def test_screen_rejects_unknown_query(screener_repository):
    with pytest.raises(ValueError, match="Unknown predefined screen"):
        screener_repository.screen("not_a_real_screen")  # type: ignore[arg-type]


def test_screen_handles_missing_response_keys(screener_repository, monkeypatch):
    """A response missing 'total' or 'quotes' entirely must not raise -
    treated as zero matches, not a construction error."""
    monkeypatch.setattr(
        "openmarkets.repositories.screener.yf.screen",
        lambda query, count=None, offset=None, session=None: {},
    )

    result = screener_repository.screen("day_gainers")

    assert result.total == 0
    assert result.quotes == []
