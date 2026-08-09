"""Real WSJ Michelangelo API tests for CommoditiesService."""

from openmarkets.schemas.commodities import CommodityHistory, CommodityQuote
from openmarkets.services.commodities import CommoditiesService
from tests.live.conftest import tolerate_network_errors


def test_get_commodity_quote_live():
    with tolerate_network_errors("WSJ Crude Oil Quote"):
        svc = CommoditiesService()
        quote = svc.get_commodity_quote("CRUDE_OIL")

        assert isinstance(quote, CommodityQuote)
        assert quote.symbol == "CRUDE_OIL"
        assert quote.price > 0
        assert quote.unit == "USD/bbl"


def test_get_gold_quote_live():
    with tolerate_network_errors("WSJ Gold Quote"):
        svc = CommoditiesService()
        quote = svc.get_commodity_quote("GOLD")

        assert isinstance(quote, CommodityQuote)
        assert quote.symbol == "GOLD"
        assert quote.price > 0
        assert quote.unit == "USD/troy oz"


def test_get_energy_prices_live():
    with tolerate_network_errors("WSJ Energy Prices"):
        svc = CommoditiesService()
        quotes = svc.get_energy_prices()

        assert isinstance(quotes, list)
        assert len(quotes) == 5
        assert any(q.symbol == "CRUDE_OIL" and q.price > 0 for q in quotes)
        assert any(q.symbol == "BRENT_CRUDE" and q.price > 0 for q in quotes)


def test_get_commodity_history_live():
    with tolerate_network_errors("WSJ Wheat History"):
        svc = CommoditiesService()
        history = svc.get_commodity_history("WHEAT", timeframe="P1M", step="P1D")

        assert isinstance(history, CommodityHistory)
        assert history.symbol == "WHEAT"
        assert len(history.data_points) > 0
        assert all(pt.close > 0 for pt in history.data_points)
