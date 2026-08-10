"""Unit tests for WSJCommoditiesRepository."""

from unittest.mock import patch

from openmarkets.repositories.commodities import WSJCommoditiesRepository


def test_get_commodity_history():
    repo = WSJCommoditiesRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000, 1616544000000]},
        "Series": [
            {
                "DataPoints": [
                    [60.0, 62.0, 59.5, 61.5],
                    [61.5, 63.0, 61.0, 62.8],
                ]
            }
        ],
    }

    with patch("openmarkets.repositories.commodities.fetch_wsj_timeseries", return_value=mock_raw):
        history = repo.get_commodity_history("CRUDE_OIL")
        assert history.symbol == "CRUDE_OIL"
        assert history.name == "Crude Oil (WTI)"
        assert len(history.data_points) == 2
        assert history.data_points[0].open == 60.0
        assert history.data_points[0].close == 61.5
        assert history.data_points[1].close == 62.8


def test_get_commodity_quote():
    repo = WSJCommoditiesRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000]},
        "Series": [{"DataPoints": [[2000.0, 2020.0, 1995.0, 2015.5]]}],
    }

    with patch("openmarkets.repositories.commodities.fetch_wsj_timeseries", return_value=mock_raw):
        quote = repo.get_commodity_quote("GOLD")
        assert quote.symbol == "GOLD"
        assert quote.price == 2015.5
        assert quote.unit == "USD/troy oz"


def test_get_energy_quotes():
    repo = WSJCommoditiesRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000]},
        "Series": [{"DataPoints": [[50.0, 52.0, 49.0, 51.0]]}],
    }

    with patch("openmarkets.repositories.commodities.fetch_wsj_timeseries", return_value=mock_raw):
        quotes = repo.get_energy_quotes()
        assert len(quotes) == 5
        assert quotes[0].symbol == "CRUDE_OIL"


def test_get_commodity_history_empty():
    repo = WSJCommoditiesRepository()
    with patch("openmarkets.repositories.commodities.fetch_wsj_timeseries", return_value={}):
        history = repo.get_commodity_history("WHEAT")
        assert history.data_points == []


def test_get_livestock_quotes():
    repo = WSJCommoditiesRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000]},
        "Series": [{"DataPoints": [[200.0, 205.0, 198.0, 202.5]]}],
    }
    with patch("openmarkets.repositories.commodities.fetch_wsj_timeseries", return_value=mock_raw):
        quotes = repo.get_livestock_quotes()
        assert len(quotes) == 3
        assert quotes[0].symbol == "LIVE_CATTLE"


def test_get_softs_quotes():
    repo = WSJCommoditiesRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000]},
        "Series": [{"DataPoints": [[100.0, 105.0, 98.0, 102.5]]}],
    }
    with patch("openmarkets.repositories.commodities.fetch_wsj_timeseries", return_value=mock_raw):
        quotes = repo.get_softs_quotes()
        assert len(quotes) == 4
        assert any(q.symbol == "COCOA" for q in quotes)
        assert any(q.symbol == "COTTON" for q in quotes)


def test_get_fertilizer_index():
    repo = WSJCommoditiesRepository()
    mock_data = [{"data": [[1616457600000, 750.25], [1617062400000, 755.50]]}]
    mock_resp = patch("openmarkets.repositories.commodities.get_session").start().return_value
    mock_resp.get.return_value.json.return_value = mock_data

    series = repo.get_fertilizer_index()
    assert series.latest_price == 755.50
    assert len(series.data_points) == 2
    assert series.data_points[0].price_index == 750.25
