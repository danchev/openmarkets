"""Real WSJ Michelangelo API tests for ForexService."""

from openmarkets.schemas.forex import ForexHistory, ForexQuote
from openmarkets.services.forex import ForexService
from tests.live.conftest import tolerate_network_errors


def test_get_forex_quote_live():
    with tolerate_network_errors("WSJ EUR/USD Quote"):
        svc = ForexService()
        quote = svc.get_forex_quote("EURUSD")

        assert isinstance(quote, ForexQuote)
        assert quote.pair == "EURUSD"
        assert quote.rate > 0
        assert quote.base_currency == "EUR"
        assert quote.quote_currency == "USD"


def test_get_dollar_index_dxy_live():
    with tolerate_network_errors("WSJ DXY Index"):
        svc = ForexService()
        dxy = svc.get_dollar_index_dxy()

        assert isinstance(dxy, ForexQuote)
        assert dxy.pair == "DXY"
        assert dxy.rate > 0


def test_get_major_currencies_live():
    with tolerate_network_errors("WSJ Major Currencies"):
        svc = ForexService()
        majors = svc.get_major_currencies()

        assert isinstance(majors, list)
        assert len(majors) == 9
        assert any(q.pair == "EURUSD" and q.rate > 0 for q in majors)
        assert any(q.pair == "USDJPY" and q.rate > 0 for q in majors)


def test_get_forex_history_live():
    with tolerate_network_errors("WSJ GBP/USD History"):
        svc = ForexService()
        history = svc.get_forex_history("GBPUSD", timeframe="P1M", step="P1D")

        assert isinstance(history, ForexHistory)
        assert history.pair == "GBPUSD"
        assert len(history.data_points) > 0
        assert all(pt.close > 0 for pt in history.data_points)
