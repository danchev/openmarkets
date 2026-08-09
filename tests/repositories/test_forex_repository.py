"""Unit tests for WSJ Forex repository."""

from unittest.mock import patch

from openmarkets.repositories.forex import WSJForexRepository
from openmarkets.schemas.forex import ForexHistory, ForexQuote


def test_get_forex_history():
    repo = WSJForexRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000, 1616544000000]},
        "Series": [
            {
                "DataPoints": [
                    [1.180, 1.185, 1.178, 1.182],
                    [1.182, 1.189, 1.181, 1.186],
                ]
            }
        ],
    }

    with patch("openmarkets.repositories.forex.fetch_wsj_timeseries", return_value=mock_raw):
        history = repo.get_forex_history("EURUSD")
        assert isinstance(history, ForexHistory)
        assert history.pair == "EURUSD"
        assert len(history.data_points) == 2
        assert history.data_points[0].close == 1.182
        assert history.data_points[1].close == 1.186


def test_get_forex_quote():
    repo = WSJForexRepository()
    mock_history = ForexHistory(
        pair="EURUSD",
        name="EUR/USD",
        data_points=[
            {
                "timestamp": 1616457600000,
                "date": "2026-08-08",
                "open": 1.180,
                "high": 1.185,
                "low": 1.178,
                "close": 1.182,
            }
        ],
    )

    with patch.object(repo, "get_forex_history", return_value=mock_history):
        quote = repo.get_forex_quote("EURUSD")
        assert isinstance(quote, ForexQuote)
        assert quote.pair == "EURUSD"
        assert quote.rate == 1.182
        assert quote.base_currency == "EUR"
        assert quote.quote_currency == "USD"


def test_get_major_currencies():
    repo = WSJForexRepository()
    mock_quote = ForexQuote(
        pair="EURUSD",
        name="EUR/USD",
        rate=1.182,
        date="2026-08-08",
        timestamp=1616457600000,
        base_currency="EUR",
        quote_currency="USD",
    )

    with patch.object(repo, "get_forex_quote", return_value=mock_quote):
        majors = repo.get_major_currencies()
        assert isinstance(majors, list)
        assert len(majors) == 9
        assert majors[0].rate == 1.182


def test_get_dollar_index_dxy():
    repo = WSJForexRepository()
    mock_quote = ForexQuote(
        pair="DXY",
        name="US Dollar Index (DXY)",
        rate=99.50,
        date="2026-08-08",
        timestamp=1616457600000,
        base_currency="DXY",
        quote_currency="USD",
    )

    with patch.object(repo, "get_forex_quote", return_value=mock_quote):
        dxy = repo.get_dollar_index_dxy()
        assert isinstance(dxy, ForexQuote)
        assert dxy.pair == "DXY"
        assert dxy.rate == 99.50
