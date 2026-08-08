"""Service-layer tests for SectorIndustryService's region parameter.

SectorIndustryService had zero service-layer tests before this file (all
prior coverage was at the repository layer). Scoped narrowly to the region
parameter added alongside it, rather than a full re-test of all 13 tools -
the repository layer already covers each tool's own logic.
"""

from unittest import mock

from openmarkets.services.sector_industry import SectorIndustryService


def _service_with_spy() -> tuple[SectorIndustryService, mock.Mock]:
    repository = mock.Mock()
    return SectorIndustryService(repository=repository), repository


def test_region_forwarded_for_every_region_scoped_tool():
    """Every tool backed by a real yfinance Sector/Industry call must
    forward the region argument through to the repository unchanged."""
    service, repository = _service_with_spy()

    service.get_sector_overview("technology", region="GB")
    repository.get_sector_overview.assert_called_once_with("technology", region="GB")

    service.get_sector_overview_for_ticker("AAPL", region="DE")
    repository.get_sector_overview_for_ticker.assert_called_once_with("AAPL", region="DE")

    service.get_sector_top_companies("technology", region="JP")
    repository.get_sector_top_companies.assert_called_once_with("technology", region="JP")

    service.get_sector_top_companies_for_ticker("AAPL", region="FR")
    repository.get_sector_top_companies_for_ticker.assert_called_once_with("AAPL", region="FR")

    service.get_sector_top_etfs("technology", region="GB")
    repository.get_sector_top_etfs.assert_called_once_with("technology", region="GB")

    service.get_sector_top_mutual_funds("technology", region="GB")
    repository.get_sector_top_mutual_funds.assert_called_once_with("technology", region="GB")

    service.get_sector_research_reports("technology", region="GB")
    repository.get_sector_research_reports.assert_called_once_with("technology", region="GB")

    service.get_industry_overview("semiconductors", region="GB")
    repository.get_industry_overview.assert_called_once_with("semiconductors", region="GB")

    service.get_industry_top_companies("semiconductors", region="GB")
    repository.get_industry_top_companies.assert_called_once_with("semiconductors", region="GB")

    service.get_industry_top_growth_companies("semiconductors", region="GB")
    repository.get_industry_top_growth_companies.assert_called_once_with("semiconductors", region="GB")

    service.get_industry_top_performing_companies("semiconductors", region="GB")
    repository.get_industry_top_performing_companies.assert_called_once_with("semiconductors", region="GB")


def test_region_defaults_to_us_when_omitted():
    """Omitting region must reproduce the pre-region-scoping call shape."""
    service, repository = _service_with_spy()

    service.get_sector_overview("technology")

    repository.get_sector_overview.assert_called_once_with("technology", region="US")


def test_static_mapping_tools_take_no_region_parameter():
    """get_sector_industries and get_all_industries are backed by a local
    mapping, not a region-scoped upstream call, so they must not accept or
    forward a region argument."""
    import inspect

    service = SectorIndustryService()

    assert "region" not in inspect.signature(service.get_sector_industries).parameters
    assert "region" not in inspect.signature(service.get_all_industries).parameters
