"""Real Yahoo Finance API tests for SectorIndustryService.

This service had zero coverage at the service layer before this file. It
also exercises the DataUnavailableError fix made in an earlier session,
though that fix triggers on upstream failure - a real success path is
tested here, and the failure path is already covered by the mocked
regression tests in tests/repositories/test_sector_industry_repository.py.
"""

from openmarkets.schemas.sector_industry import (
    IndustryOverview,
    IndustryResearchReportEntry,
    IndustryTopCompaniesEntry,
    IndustryTopGrowthCompaniesEntry,
    IndustryTopPerformingCompaniesEntry,
    SectorOverview,
    SectorTopCompaniesEntry,
    SectorTopETFsEntry,
    SectorTopMutualFundsEntry,
)
from openmarkets.services.sector_industry import SectorIndustryService
from tests.live.conftest import STABLE_INDUSTRY, STABLE_SECTOR, STABLE_TICKER, tolerate_network_errors


def test_get_sector_overview_against_real_api():
    with tolerate_network_errors("get_sector_overview"):
        result = SectorIndustryService().get_sector_overview(STABLE_SECTOR)

    assert isinstance(result, SectorOverview)


def test_get_sector_overview_for_ticker_against_real_api():
    with tolerate_network_errors("get_sector_overview_for_ticker"):
        result = SectorIndustryService().get_sector_overview_for_ticker(STABLE_TICKER)

    assert isinstance(result, SectorOverview)


def test_get_sector_top_companies_against_real_api():
    with tolerate_network_errors("get_sector_top_companies"):
        result = SectorIndustryService().get_sector_top_companies(STABLE_SECTOR)

    assert isinstance(result, list)
    assert all(isinstance(entry, SectorTopCompaniesEntry) for entry in result)


def test_get_sector_top_companies_for_ticker_against_real_api():
    with tolerate_network_errors("get_sector_top_companies_for_ticker"):
        result = SectorIndustryService().get_sector_top_companies_for_ticker(STABLE_TICKER)

    assert isinstance(result, list)


def test_get_sector_top_etfs_against_real_api():
    with tolerate_network_errors("get_sector_top_etfs"):
        result = SectorIndustryService().get_sector_top_etfs(STABLE_SECTOR)

    assert isinstance(result, list)
    assert all(isinstance(entry, SectorTopETFsEntry) for entry in result)


def test_get_sector_top_mutual_funds_against_real_api():
    with tolerate_network_errors("get_sector_top_mutual_funds"):
        result = SectorIndustryService().get_sector_top_mutual_funds(STABLE_SECTOR)

    assert isinstance(result, list)
    assert all(isinstance(entry, SectorTopMutualFundsEntry) for entry in result)


def test_get_sector_industries_against_real_api():
    result = SectorIndustryService().get_sector_industries(STABLE_SECTOR)

    assert isinstance(result, list)
    assert all(isinstance(entry, str) for entry in result)


def test_get_sector_research_reports_against_real_api():
    with tolerate_network_errors("get_sector_research_reports"):
        result = SectorIndustryService().get_sector_research_reports(STABLE_SECTOR)

    assert isinstance(result, list)
    assert all(isinstance(entry, IndustryResearchReportEntry) for entry in result)


def test_get_all_industries_against_real_api():
    result = SectorIndustryService().get_all_industries()

    assert isinstance(result, list)
    assert len(result) > 0


def test_get_industry_overview_against_real_api():
    with tolerate_network_errors("get_industry_overview"):
        result = SectorIndustryService().get_industry_overview(STABLE_INDUSTRY)

    assert isinstance(result, IndustryOverview)


def test_get_industry_top_companies_against_real_api():
    with tolerate_network_errors("get_industry_top_companies"):
        result = SectorIndustryService().get_industry_top_companies(STABLE_INDUSTRY)

    assert isinstance(result, list)
    assert all(isinstance(entry, IndustryTopCompaniesEntry) for entry in result)


def test_get_industry_top_growth_companies_against_real_api():
    with tolerate_network_errors("get_industry_top_growth_companies"):
        result = SectorIndustryService().get_industry_top_growth_companies(STABLE_INDUSTRY)

    assert isinstance(result, list)
    assert all(isinstance(entry, IndustryTopGrowthCompaniesEntry) for entry in result)


def test_get_industry_top_performing_companies_against_real_api():
    with tolerate_network_errors("get_industry_top_performing_companies"):
        result = SectorIndustryService().get_industry_top_performing_companies(STABLE_INDUSTRY)

    assert isinstance(result, list)
    assert all(isinstance(entry, IndustryTopPerformingCompaniesEntry) for entry in result)


def test_region_scoping_returns_different_companies_against_real_api():
    """Verifies the region parameter added alongside this test file:
    yf.Sector defaults to US-scoped data, and every one of these tools
    previously had no way to request a different regional exchange."""
    service = SectorIndustryService()

    us_companies = service.get_sector_top_companies(STABLE_SECTOR, region="US")
    gb_companies = service.get_sector_top_companies(STABLE_SECTOR, region="GB")

    assert us_companies
    assert gb_companies
    us_symbols = {entry.symbol for entry in us_companies}
    gb_symbols = {entry.symbol for entry in gb_companies}
    assert us_symbols != gb_symbols
