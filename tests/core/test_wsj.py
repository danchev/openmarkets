"""Unit tests for WSJ Michelangelo client adapter."""

from unittest.mock import Mock

import pytest

from openmarkets.core.exceptions import ProviderContractError
from openmarkets.core.wsj import (
    _build_wsj_headers,
    fetch_wsj_timeseries,
    resolve_wsj_key,
)


def test_resolve_wsj_key():
    key, name, exch, unit = resolve_wsj_key("CRUDE_OIL")
    assert key == "FUTURE/US/XNYM/CL00"
    assert name == "Crude Oil (WTI)"
    assert exch == "NYMEX"
    assert unit == "USD/bbl"

    key_gold, name_gold, _, _ = resolve_wsj_key("gold")
    assert key_gold == "FUTURE/US/XNYM/GC00"
    assert name_gold == "Gold"

    key_10y, name_10y, _, _ = resolve_wsj_key("US10Y")
    assert key_10y == "BOND/BX/XTUP/TMUBMUSD10Y"
    assert "10-Year" in name_10y

    # Raw key pass-through
    raw_key, _, _, _ = resolve_wsj_key("FUTURE/US/XCBT/W00")
    assert raw_key == "FUTURE/US/XCBT/W00"

    # Default stock fallback
    stock_key, stock_name, _, _ = resolve_wsj_key("NVDA")
    assert stock_key == "STOCK/US//NVDA"
    assert stock_name == "NVDA"


def test_build_wsj_headers():
    headers = _build_wsj_headers("custom-token")
    assert headers["Dylan2010.EntitlementToken"] == "custom-token"
    assert "Mozilla" in headers["User-Agent"]


def test_fetch_wsj_timeseries_success():
    session_mock = Mock()
    resp_mock = Mock()
    resp_mock.json.return_value = {
        "TimeInfo": {"Ticks": [1616457600000]},
        "Series": [{"DataPoints": [[100.0, 105.0, 99.0, 102.0]]}],
    }
    resp_mock.raise_for_status.return_value = None
    session_mock.get.return_value = resp_mock

    result = fetch_wsj_timeseries("FUTURE/US/XNYM/CL00", session=session_mock)
    assert "TimeInfo" in result
    assert result["TimeInfo"]["Ticks"] == [1616457600000]
    session_mock.get.assert_called_once()


def test_fetch_wsj_timeseries_rejects_non_object_payload():
    session_mock = Mock()
    session_mock.get.return_value.json.return_value = []

    with pytest.raises(ProviderContractError, match="expected a JSON object"):
        fetch_wsj_timeseries("STOCK/US//AAPL", session=session_mock)


@pytest.mark.parametrize(("key", "step", "timeframe"), [("", "P1D", "P1Y"), ("AAPL", "", "P1Y"), ("AAPL", "P1D", "")])
def test_fetch_wsj_timeseries_rejects_empty_request_fields(key, step, timeframe):
    with pytest.raises(ValueError):
        fetch_wsj_timeseries(key, step=step, timeframe=timeframe, session=Mock())


def test_normalize_wsj_timeframe():
    from openmarkets.core.wsj import normalize_wsj_timeframe

    assert normalize_wsj_timeframe("1y") == "P1Y"
    assert normalize_wsj_timeframe("1mo") == "P1M"
    assert normalize_wsj_timeframe("5y") == "P5Y"
    assert normalize_wsj_timeframe("7d") == "D7"
    assert normalize_wsj_timeframe("max") == "all"
    assert normalize_wsj_timeframe("P3M") == "P3M"
