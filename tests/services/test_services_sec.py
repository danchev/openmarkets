"""Unit tests for SECService delegation."""

from unittest.mock import MagicMock

from openmarkets.services.sec import SECService


def test_sec_service_delegation():
    mock_repo = MagicMock()
    service = SECService(repository=mock_repo)

    service.get_sec_company_profile("AAPL")
    mock_repo.get_company_profile.assert_called_once_with(ticker="AAPL", session=service.session)

    service.get_sec_recent_filings("AAPL", form_type="10-K", limit=10)
    mock_repo.get_recent_filings.assert_called_once_with(
        ticker="AAPL", form_type="10-K", limit=10, session=service.session
    )

    service.get_sec_10k_annual_filings("AAPL", limit=3)
    mock_repo.get_10k_annual_filings.assert_called_once_with(ticker="AAPL", limit=3, session=service.session)

    service.get_sec_10q_quarterly_filings("AAPL", limit=4)
    mock_repo.get_10q_quarterly_filings.assert_called_once_with(ticker="AAPL", limit=4, session=service.session)

    service.get_sec_8k_material_events("AAPL", limit=6)
    mock_repo.get_8k_material_events.assert_called_once_with(ticker="AAPL", limit=6, session=service.session)

    service.get_sec_insider_form4_filings("AAPL", limit=8)
    mock_repo.get_insider_form4_filings.assert_called_once_with(ticker="AAPL", limit=8, session=service.session)

    service.get_sec_xbrl_company_facts("AAPL")
    mock_repo.get_xbrl_facts_summary.assert_called_once_with(ticker="AAPL", session=service.session)

    service.get_sec_xbrl_concept_timeseries("AAPL", concept="REVENUES", limit=12)
    mock_repo.get_xbrl_concept_timeseries.assert_called_once_with(
        ticker="AAPL", concept="REVENUES", limit=12, session=service.session
    )

    service.get_sec_cik_lookup("Apple", limit=5)
    mock_repo.search_cik.assert_called_once_with(query="Apple", limit=5, session=service.session)


def test_sec_service_tool_count():
    service = SECService()
    assert len(service.tool_names()) == 9
