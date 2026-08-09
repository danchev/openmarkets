"""Unit tests for WSJStockRepository."""

from unittest.mock import patch

from openmarkets.repositories.stock import WSJStockRepository
from openmarkets.schemas.stock import WSJBollingerBandsSeries, WSJStockHistory


def test_wsj_get_stock_history():
    repo = WSJStockRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000, 1616544000000]},
        "Series": [
            {
                "DataPoints": [
                    [150.0, 155.0, 149.0, 153.5],
                    [153.5, 158.0, 152.0, 157.2],
                ]
            },
            {
                "DataPoints": [
                    [1000000.0],
                    [1200000.0],
                ]
            },
        ],
    }

    with patch("openmarkets.repositories.stock.fetch_wsj_timeseries", return_value=mock_raw):
        history = repo.get_stock_history("AAPL")
        assert isinstance(history, WSJStockHistory)
        assert history.symbol == "AAPL"
        assert len(history.data_points) == 2
        assert history.data_points[0].open == 150.0
        assert history.data_points[0].close == 153.5
        assert history.data_points[0].volume == 1000000.0
        assert history.data_points[1].close == 157.2
        assert history.data_points[1].volume == 1200000.0


def test_wsj_get_bollinger_bands():
    repo = WSJStockRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000]},
        "Series": [
            {"DataPoints": [[153.5]]},
            {"DataPoints": [[145.0, 150.0, 155.0]]},
        ],
    }

    with patch("openmarkets.repositories.stock.fetch_wsj_timeseries", return_value=mock_raw):
        bb = repo.get_bollinger_bands("AAPL", window=20, multiplier=2.0)
        assert isinstance(bb, WSJBollingerBandsSeries)
        assert bb.symbol == "AAPL"
        assert bb.window == 20
        assert len(bb.data_points) == 1
        pt = bb.data_points[0]
        assert pt.price == 153.5
        assert pt.lower_band == 145.0
        assert pt.middle_band == 150.0
        assert pt.upper_band == 155.0
        # (155 - 145) / 150 * 100 = 6.67%
        assert pt.bandwidth_pct == 6.67
