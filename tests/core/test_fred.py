"""Unit tests for openmarkets.core.fred client utilities."""

from unittest.mock import Mock

import pytest

from openmarkets.core.fred import FRED_SERIES_CATALOG, fetch_fred_timeseries


def test_fred_series_catalog_contains_expected_series():
    assert "CPIAUCSL" in FRED_SERIES_CATALOG
    assert "PCEPILFE" in FRED_SERIES_CATALOG
    assert "FEDFUNDS" in FRED_SERIES_CATALOG
    assert "UNRATE" in FRED_SERIES_CATALOG
    assert "GDPC1" in FRED_SERIES_CATALOG
    assert "M2SL" in FRED_SERIES_CATALOG
    assert "T10YIE" in FRED_SERIES_CATALOG


def test_fetch_fred_timeseries_success():
    session_mock = Mock()
    resp_mock = Mock()
    resp_mock.status_code = 200
    resp_mock.text = """observation_date,CPIAUCSL
2026-04-01,330.123
2026-05-01,.
2026-06-01,332.568
"""
    session_mock.get.return_value = resp_mock

    results = fetch_fred_timeseries("CPIAUCSL", session=session_mock)
    assert len(results) == 2
    assert results[0] == {"date": "2026-04-01", "value": 330.123}
    assert results[1] == {"date": "2026-06-01", "value": 332.568}


def test_fetch_fred_timeseries_http_error():
    session_mock = Mock()
    resp_mock = Mock()
    resp_mock.status_code = 404
    session_mock.get.return_value = resp_mock

    with pytest.raises(ValueError, match="HTTP 404"):
        fetch_fred_timeseries("INVALID_SERIES", session=session_mock)


def test_fetch_fred_timeseries_network_error():
    session_mock = Mock()
    session_mock.get.side_effect = ConnectionError("Network unreachable")

    with pytest.raises(ValueError, match="Failed to fetch"):
        fetch_fred_timeseries("CPIAUCSL", session=session_mock)


def test_fetch_fred_timeseries_empty():
    session_mock = Mock()
    resp_mock = Mock()
    resp_mock.status_code = 200
    resp_mock.text = "observation_date,CPIAUCSL\n"
    session_mock.get.return_value = resp_mock

    with pytest.raises(ValueError, match="Empty or invalid response"):
        fetch_fred_timeseries("CPIAUCSL", session=session_mock)
