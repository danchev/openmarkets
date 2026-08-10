"""Unit tests for CommoditiesService."""

from unittest.mock import Mock

from openmarkets.schemas.commodities import CommodityHistory, CommodityQuote
from openmarkets.services.commodities import CommoditiesService


def test_commodities_service_delegation():
    repo_mock = Mock()
    repo_mock.get_commodity_quote.return_value = CommodityQuote(
        symbol="CRUDE_OIL",
        name="Crude Oil (WTI)",
        exchange="NYMEX",
        unit="USD/bbl",
        price=75.50,
        date="2026-08-09",
    )
    repo_mock.get_commodity_history.return_value = CommodityHistory(
        symbol="CRUDE_OIL",
        name="Crude Oil (WTI)",
        exchange="NYMEX",
        unit="USD/bbl",
        data_points=[],
    )
    repo_mock.get_energy_quotes.return_value = []
    repo_mock.get_metals_quotes.return_value = []
    repo_mock.get_agriculture_quotes.return_value = []
    repo_mock.get_livestock_quotes.return_value = []
    repo_mock.get_softs_quotes.return_value = []
    repo_mock.get_fertilizer_index.return_value = None

    service = CommoditiesService(repository=repo_mock)

    quote = service.get_commodity_quote("CRUDE_OIL")
    assert quote.price == 75.50

    history = service.get_commodity_history("CRUDE_OIL", timeframe="P1Y")
    assert history.symbol == "CRUDE_OIL"

    assert service.get_energy_prices() == []
    assert service.get_metals_prices() == []
    assert service.get_agriculture_prices() == []
    assert service.get_livestock_prices() == []
    assert service.get_softs_prices() == []
    assert service.get_fertilizer_price_index() is None
