"""Unit tests for SEC EDGAR core client layer."""

from unittest.mock import MagicMock

import pytest

from openmarkets.core.exceptions import DataUnavailableError, InvalidSymbolError
from openmarkets.core.sec import (
    build_sec_doc_url,
    fetch_sec_company_facts,
    fetch_sec_concept,
    fetch_sec_submissions,
    resolve_cik,
    search_sec_entities,
)


def test_build_sec_doc_url():
    url = build_sec_doc_url("0000320193", "0000320193-26-000020", "aapl-20260627.htm")
    assert url == "https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/aapl-20260627.htm"


def test_resolve_cik_pure_digits():
    cik, title = resolve_cik("320193")
    assert cik == "0000320193"
    assert "320193" in title


def test_resolve_cik_ticker():
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
        "1": {"cik_str": 789019, "ticker": "MSFT", "title": "Microsoft Corp"},
    }
    mock_session.get.return_value = mock_resp

    cik, title = resolve_cik("AAPL", session=mock_session)
    assert cik == "0000320193"
    assert title == "Apple Inc."


def test_resolve_cik_invalid():
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {}
    mock_session.get.return_value = mock_resp

    with pytest.raises(InvalidSymbolError):
        resolve_cik("COMPLETELY_INVALID_TICKER_XYZ", session=mock_session)


def test_fetch_sec_submissions():
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"name": "Apple Inc.", "sic": "3571"}
    mock_session.get.return_value = mock_resp

    data = fetch_sec_submissions("0000320193", session=mock_session)
    assert data["name"] == "Apple Inc."
    assert data["sic"] == "3571"


def test_fetch_sec_submissions_404():
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_session.get.return_value = mock_resp

    with pytest.raises(DataUnavailableError):
        fetch_sec_submissions("0000000000", session=mock_session)


def test_fetch_sec_company_facts():
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"entityName": "Apple Inc.", "facts": {"us-gaap": {}}}
    mock_session.get.return_value = mock_resp

    data = fetch_sec_company_facts("0000320193", session=mock_session)
    assert data["entityName"] == "Apple Inc."


def test_fetch_sec_concept():
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"label": "Revenues", "units": {"USD": []}}
    mock_session.get.return_value = mock_resp

    data = fetch_sec_concept("0000320193", concept="Revenues", session=mock_session)
    assert data["label"] == "Revenues"


def test_search_sec_entities():
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
        "1": {"cik_str": 789019, "ticker": "MSFT", "title": "Microsoft Corp"},
    }
    mock_session.get.return_value = mock_resp

    res = search_sec_entities("Apple", limit=5, session=mock_session)
    assert len(res) >= 1
    assert res[0]["ticker"] == "AAPL"
