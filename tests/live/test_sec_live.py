"""Live API tests for SEC EDGAR regulatory tools against real SEC endpoints."""

import pytest

from openmarkets.schemas.sec import (
    SECCIKLookupResult,
    SECCompanyProfile,
    SECFilingItem,
    SECXBRLCompanyFactsSummary,
    SECXBRLConceptTimeseries,
)
from openmarkets.services.sec import sec_service


@pytest.mark.live
def test_live_get_sec_company_profile():
    profile = sec_service.get_sec_company_profile("AAPL")
    assert isinstance(profile, SECCompanyProfile)
    assert profile.ticker == "AAPL"
    assert profile.cik == "0000320193"
    assert profile.sic == "3571"
    assert "Apple" in profile.name
    assert profile.business_address is not None
    assert profile.business_address.city == "Cupertino"


@pytest.mark.live
def test_live_get_sec_recent_filings():
    filings = sec_service.get_sec_recent_filings("AAPL", limit=5)
    assert isinstance(filings, list)
    assert len(filings) > 0
    assert all(isinstance(f, SECFilingItem) for f in filings)
    assert filings[0].document_url.startswith("https://www.sec.gov/Archives/edgar/data/320193/")


@pytest.mark.live
def test_live_get_sec_10k_filings():
    filings = sec_service.get_sec_10k_annual_filings("AAPL", limit=2)
    assert isinstance(filings, list)
    assert len(filings) > 0
    assert all(f.form == "10-K" for f in filings)


@pytest.mark.live
def test_live_get_sec_10q_filings():
    filings = sec_service.get_sec_10q_quarterly_filings("AAPL", limit=3)
    assert isinstance(filings, list)
    assert len(filings) > 0
    assert all(f.form == "10-Q" for f in filings)


@pytest.mark.live
def test_live_get_sec_8k_material_events():
    filings = sec_service.get_sec_8k_material_events("AAPL", limit=4)
    assert isinstance(filings, list)
    assert len(filings) > 0
    assert all(f.form == "8-K" for f in filings)


@pytest.mark.live
def test_live_get_sec_insider_form4_filings():
    filings = sec_service.get_sec_insider_form4_filings("AAPL", limit=5)
    assert isinstance(filings, list)
    assert len(filings) > 0
    assert all(f.form == "4" for f in filings)


@pytest.mark.live
def test_live_get_sec_xbrl_company_facts():
    facts = sec_service.get_sec_xbrl_company_facts("AAPL")
    assert isinstance(facts, SECXBRLCompanyFactsSummary)
    assert facts.available_gaap_concepts_count > 100
    assert "REVENUES" in facts.key_metrics_available


@pytest.mark.live
def test_live_get_sec_xbrl_concept_timeseries():
    ts = sec_service.get_sec_xbrl_concept_timeseries("AAPL", concept="REVENUES", limit=8)
    assert isinstance(ts, SECXBRLConceptTimeseries)
    assert ts.latest_value is not None and ts.latest_value > 0
    assert len(ts.observations) > 0


@pytest.mark.live
def test_live_get_sec_cik_lookup():
    matches = sec_service.get_sec_cik_lookup("Microsoft", limit=3)
    assert isinstance(matches, list)
    assert len(matches) > 0
    assert all(isinstance(m, SECCIKLookupResult) for m in matches)
    assert any(m.ticker == "MSFT" for m in matches)
