"""Unit tests for SEC EDGAR repository layer."""

from unittest.mock import patch

from openmarkets.repositories.sec import SECEDGARRepository
from openmarkets.schemas.sec import (
    SECCIKLookupResult,
    SECCompanyProfile,
    SECFilingItem,
    SECXBRLCompanyFactsSummary,
    SECXBRLConceptTimeseries,
)

SAMPLE_SUBMISSIONS = {
    "name": "Apple Inc.",
    "sic": "3571",
    "sicDescription": "Electronic Computers",
    "fiscalYearEnd": "0930",
    "stateOfIncorporationDescription": "California",
    "addresses": {
        "business": {
            "street1": "One Apple Park Way",
            "city": "Cupertino",
            "stateOrCountryDescription": "CA",
            "zipCode": "95014",
        }
    },
    "filings": {
        "recent": {
            "form": ["10-Q", "8-K", "4", "10-K"],
            "filingDate": ["2026-07-31", "2026-07-30", "2026-06-17", "2025-11-01"],
            "reportDate": ["2026-06-27", "2026-07-30", None, "2025-09-30"],
            "accessionNumber": [
                "0000320193-26-000020",
                "0000320193-26-000018",
                "0001140361-26-025622",
                "0000320193-25-000100",
            ],
            "primaryDocument": [
                "aapl-20260627.htm",
                "aapl-20260730.htm",
                "form4.xml",
                "aapl-20250930.htm",
            ],
            "primaryDocDescription": ["10-Q", "8-K", "FORM 4", "10-K"],
            "isXBRL": [1, 0, 0, 1],
        }
    },
}

SAMPLE_FACTS = {
    "entityName": "Apple Inc.",
    "facts": {
        "us-gaap": {
            "Revenues": {
                "label": "Revenue",
                "description": "Total revenue",
                "units": {
                    "USD": [
                        {"end": "2026-03-28", "val": 90000000000, "fy": 2026, "fp": "Q2", "form": "10-Q"},
                        {"end": "2026-06-27", "val": 95000000000, "fy": 2026, "fp": "Q3", "form": "10-Q"},
                    ]
                },
            },
            "Assets": {
                "label": "Total Assets",
                "units": {"USD": [{"end": "2026-06-27", "val": 350000000000, "fy": 2026, "fp": "Q3", "form": "10-Q"}]},
            },
        }
    },
}


def test_get_company_profile():
    repo = SECEDGARRepository()
    with patch("openmarkets.repositories.sec.resolve_cik", return_value=("0000320193", "Apple Inc.")):
        with patch("openmarkets.repositories.sec.fetch_sec_submissions", return_value=SAMPLE_SUBMISSIONS):
            profile = repo.get_company_profile("AAPL")
            assert isinstance(profile, SECCompanyProfile)
            assert profile.ticker == "AAPL"
            assert profile.cik == "0000320193"
            assert profile.sic == "3571"
            assert profile.business_address is not None
            assert profile.business_address.city == "Cupertino"


def test_get_recent_filings():
    repo = SECEDGARRepository()
    with patch("openmarkets.repositories.sec.resolve_cik", return_value=("0000320193", "Apple Inc.")):
        with patch("openmarkets.repositories.sec.fetch_sec_submissions", return_value=SAMPLE_SUBMISSIONS):
            filings = repo.get_recent_filings("AAPL", limit=10)
            assert len(filings) == 4
            assert all(isinstance(f, SECFilingItem) for f in filings)
            assert filings[0].form == "10-Q"
            assert filings[0].document_url.startswith("https://www.sec.gov/Archives/edgar/data/320193/")


def test_get_filtered_filings():
    repo = SECEDGARRepository()
    with patch("openmarkets.repositories.sec.resolve_cik", return_value=("0000320193", "Apple Inc.")):
        with patch("openmarkets.repositories.sec.fetch_sec_submissions", return_value=SAMPLE_SUBMISSIONS):
            ten_k = repo.get_10k_annual_filings("AAPL", limit=5)
            assert len(ten_k) == 1
            assert ten_k[0].form == "10-K"

            ten_q = repo.get_10q_quarterly_filings("AAPL", limit=5)
            assert len(ten_q) == 1
            assert ten_q[0].form == "10-Q"

            eight_k = repo.get_8k_material_events("AAPL", limit=5)
            assert len(eight_k) == 1
            assert eight_k[0].form == "8-K"

            form4 = repo.get_insider_form4_filings("AAPL", limit=5)
            assert len(form4) == 1
            assert form4[0].form == "4"


def test_get_xbrl_facts_summary():
    repo = SECEDGARRepository()
    with patch("openmarkets.repositories.sec.resolve_cik", return_value=("0000320193", "Apple Inc.")):
        with patch("openmarkets.repositories.sec.fetch_sec_company_facts", return_value=SAMPLE_FACTS):
            summary = repo.get_xbrl_facts_summary("AAPL")
            assert isinstance(summary, SECXBRLCompanyFactsSummary)
            assert summary.available_gaap_concepts_count == 2
            assert "REVENUES" in summary.key_metrics_available
            assert "ASSETS" in summary.key_metrics_available


def test_get_xbrl_concept_timeseries():
    repo = SECEDGARRepository()
    with patch("openmarkets.repositories.sec.resolve_cik", return_value=("0000320193", "Apple Inc.")):
        with patch("openmarkets.repositories.sec.fetch_sec_company_facts", return_value=SAMPLE_FACTS):
            series = repo.get_xbrl_concept_timeseries("AAPL", concept="REVENUES", limit=10)
            assert isinstance(series, SECXBRLConceptTimeseries)
            assert series.concept == "Revenues"
            assert series.latest_value == 95000000000
            assert len(series.observations) == 2


def test_search_cik():
    repo = SECEDGARRepository()
    with patch(
        "openmarkets.repositories.sec.search_sec_entities",
        return_value=[{"ticker": "AAPL", "cik": "0000320193", "title": "Apple Inc."}],
    ):
        results = repo.search_cik("Apple")
        assert len(results) == 1
        assert isinstance(results[0], SECCIKLookupResult)
        assert results[0].ticker == "AAPL"
