"""Unit tests for WSJMarketsRepository."""

from unittest.mock import patch

from openmarkets.repositories.markets import WSJMarketsRepository
from openmarkets.schemas.markets import GlobalIndexQuote, GlobalMarketSnapshot


def test_wsj_get_global_indices():
    repo = WSJMarketsRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000]},
        "Series": [{"DataPoints": [[5000.25]]}],
    }

    with patch("openmarkets.repositories.markets.fetch_wsj_timeseries", return_value=mock_raw):
        snapshot = repo.get_global_indices()
        assert isinstance(snapshot, GlobalMarketSnapshot)
        assert len(snapshot.indices) > 0
        assert all(isinstance(q, GlobalIndexQuote) for q in snapshot.indices)
        spx = next((q for q in snapshot.indices if q.symbol == "SP500"), None)
        assert spx is not None
        assert spx.value == 5000.25


def test_wsj_get_volatility_vix():
    repo = WSJMarketsRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000]},
        "Series": [{"DataPoints": [[15.42]]}],
    }

    with patch("openmarkets.repositories.markets.fetch_wsj_timeseries", return_value=mock_raw):
        vix = repo.get_volatility_vix()
        assert isinstance(vix, GlobalIndexQuote)
        assert vix.symbol == "VIX"
        assert vix.value == 15.42
