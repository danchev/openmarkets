"""Unit tests for WSJTechnicalAnalysisRepository."""

from unittest.mock import patch

from openmarkets.repositories.technical_analysis import WSJTechnicalAnalysisRepository
from openmarkets.schemas.technical_analysis import WSJIndicatorSeries, WSJMACDSeries


def test_wsj_get_sma():
    repo = WSJTechnicalAnalysisRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000]},
        "Series": [
            {"DataPoints": [[150.0]]},
            {"DataPoints": [[148.5]]},
        ],
    }

    with patch("openmarkets.repositories.technical_analysis.fetch_wsj_timeseries", return_value=mock_raw):
        res = repo.get_sma("AAPL", window=50)
        assert isinstance(res, WSJIndicatorSeries)
        assert res.symbol == "AAPL"
        assert res.indicator == "SMA"
        assert res.window == 50
        assert len(res.data_points) == 1
        assert res.data_points[0].price == 150.0
        assert res.data_points[0].value == 148.5


def test_wsj_get_ema():
    repo = WSJTechnicalAnalysisRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000]},
        "Series": [
            {"DataPoints": [[150.0]]},
            {"DataPoints": [[149.2]]},
        ],
    }

    with patch("openmarkets.repositories.technical_analysis.fetch_wsj_timeseries", return_value=mock_raw):
        res = repo.get_ema("AAPL", window=20)
        assert isinstance(res, WSJIndicatorSeries)
        assert res.indicator == "EMA"
        assert res.window == 20
        assert res.data_points[0].value == 149.2


def test_wsj_get_rsi():
    repo = WSJTechnicalAnalysisRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000]},
        "Series": [
            {"DataPoints": [[150.0]]},
            {"DataPoints": [[55.4]]},
        ],
    }

    with patch("openmarkets.repositories.technical_analysis.fetch_wsj_timeseries", return_value=mock_raw):
        res = repo.get_rsi("AAPL", window=14)
        assert isinstance(res, WSJIndicatorSeries)
        assert res.indicator == "RSI"
        assert res.window == 14
        assert res.data_points[0].value == 55.4


def test_wsj_get_macd():
    repo = WSJTechnicalAnalysisRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000]},
        "Series": [
            {"DataPoints": [[150.0]]},
            {"DataPoints": [[1.25, 0.85, 0.40]]},
        ],
    }

    with patch("openmarkets.repositories.technical_analysis.fetch_wsj_timeseries", return_value=mock_raw):
        res = repo.get_macd("AAPL", fast_window=12, slow_window=26, signal_window=9)
        assert isinstance(res, WSJMACDSeries)
        assert res.symbol == "AAPL"
        assert len(res.data_points) == 1
        pt = res.data_points[0]
        assert pt.macd == 1.25
        assert pt.signal == 0.85
        assert pt.histogram == 0.40
