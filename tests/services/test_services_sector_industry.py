"""Tests for SectorIndustryService delegation to repository."""

from __future__ import annotations

from collections.abc import Iterable
from typing import cast

import pytest
from curl_cffi.requests import Session

from openmarkets.repositories.sector_industry import ISectorIndustryRepository
from openmarkets.services.sector_industry import SectorIndustryService
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


class SectorIndustryRepositorySpy(ISectorIndustryRepository):
    """A minimal spy for SectorIndustryService delegation tests."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def get_sector_overview(self, sector: str, session: Session | None = None) -> SectorOverview:
        self.calls.append(("get_sector_overview", sector, session))
        return SectorOverview(
            companies_count=100,
            market_cap=1000000,
            message_board_id="mb_123",
            description=f"Overview for {sector}",
            industries_count=10,
            market_weight=0.25,
            employee_count=500000,
        )

    def get_sector_overview_for_ticker(self, ticker: str, session: Session | None = None) -> SectorOverview:
        self.calls.append(("get_sector_overview_for_ticker", ticker, session))
        return SectorOverview(
            companies_count=100,
            market_cap=1000000,
            message_board_id="mb_123",
            description="Tech sector",
            industries_count=10,
            market_weight=0.25,
            employee_count=500000,
        )

    def get_sector_top_companies(self, sector: str, session: Session | None = None) -> list[SectorTopCompaniesEntry]:
        self.calls.append(("get_sector_top_companies", sector, session))
        return [SectorTopCompaniesEntry(symbol="AAPL", name="Apple", rating="A", **{"market weight": 0.15})]

    def get_sector_top_companies_for_ticker(
        self, ticker: str, session: Session | None = None
    ) -> list[SectorTopCompaniesEntry]:
        self.calls.append(("get_sector_top_companies_for_ticker", ticker, session))
        return [SectorTopCompaniesEntry(symbol="AAPL", name="Apple", rating="A", **{"market weight": 0.15})]

    def get_sector_top_etfs(self, sector: str, session: Session | None = None) -> list[SectorTopETFsEntry]:
        self.calls.append(("get_sector_top_etfs", sector, session))
        return [SectorTopETFsEntry(symbol="XLK", name="Tech ETF")]

    def get_sector_top_mutual_funds(
        self, sector: str, session: Session | None = None
    ) -> list[SectorTopMutualFundsEntry]:
        self.calls.append(("get_sector_top_mutual_funds", sector, session))
        return [SectorTopMutualFundsEntry(symbol="VFINX", name="S&P 500 Fund")]

    def get_sector_industries(self, sector: str, session: Session | None = None) -> list[str]:
        self.calls.append(("get_sector_industries", sector, session))
        return ["Software", "Hardware"]

    def get_sector_research_reports(
        self, sector: str, session: Session | None = None
    ) -> list[IndustryResearchReportEntry]:
        self.calls.append(("get_sector_research_reports", sector, session))
        return [
            IndustryResearchReportEntry(
                id="report_1",
                **{"headHtml": "<h1>Tech Report</h1>", "provider": "Yahoo", "reportTitle": "Tech Sector Report", "reportType": "analysis"},
            )
        ]

    def get_all_industries(self, sector: str | None = None, session: Session | None = None) -> list[str]:
        self.calls.append(("get_all_industries", sector, session))
        return ["Software", "Hardware", "Biotech"]

    def get_industry_overview(self, industry: str, session: Session | None = None) -> IndustryOverview:
        self.calls.append(("get_industry_overview", industry, session))
        return IndustryOverview(
            companies_count=50,
            market_cap=500000,
            message_board_id="mb_456",
            description=f"Overview for {industry}",
            market_weight=0.10,
            employee_count=250000,
        )

    def get_industry_top_companies(
        self, industry: str, session: Session | None = None
    ) -> list[IndustryTopCompaniesEntry]:
        self.calls.append(("get_industry_top_companies", industry, session))
        return [IndustryTopCompaniesEntry(symbol="MSFT", name="Microsoft", rating="A", **{"market weight": 0.20})]

    def get_industry_top_growth_companies(
        self, industry: str, session: Session | None = None
    ) -> list[IndustryTopGrowthCompaniesEntry]:
        self.calls.append(("get_industry_top_growth_companies", industry, session))
        return [IndustryTopGrowthCompaniesEntry(symbol="NVDA", name="NVIDIA", **{"ytd return": 0.50, "growth estimate": 0.25})]

    def get_industry_top_performing_companies(
        self, industry: str, session: Session | None = None
    ) -> list[IndustryTopPerformingCompaniesEntry]:
        self.calls.append(("get_industry_top_performing_companies", industry, session))
        return [IndustryTopPerformingCompaniesEntry(symbol="GOOGL", name="Google", **{"ytd return": 0.30, "last price": 150.0, "target price": 180.0})]


@pytest.fixture
def sector_industry_repository_spy() -> SectorIndustryRepositorySpy:
    return SectorIndustryRepositorySpy()


@pytest.fixture
def sector_industry_service(sector_industry_repository_spy: SectorIndustryRepositorySpy) -> SectorIndustryService:
    session_sentinel = cast(Session, object())
    return SectorIndustryService(repository=sector_industry_repository_spy)


def test_sector_industry_service_delegates_to_repository(
    sector_industry_service: SectorIndustryService,
    sector_industry_repository_spy: SectorIndustryRepositorySpy,
) -> None:
    """Test that all service methods delegate correctly to the repository."""
    sector = "Technology"
    industry = "Software"
    ticker = "AAPL"

    # Sector overview
    result = sector_industry_service.get_sector_overview(sector)
    assert result.description == f"Overview for {sector}"
    assert result.companies_count == 100

    # Sector overview for ticker
    result = sector_industry_service.get_sector_overview_for_ticker(ticker)
    assert result.description == "Tech sector"

    # Sector top companies
    result = sector_industry_service.get_sector_top_companies(sector)
    assert len(result) == 1
    assert result[0].symbol == "AAPL"

    # Sector top companies for ticker
    result = sector_industry_service.get_sector_top_companies_for_ticker(ticker)
    assert len(result) == 1
    assert result[0].symbol == "AAPL"

    # Sector top ETFs
    result = sector_industry_service.get_sector_top_etfs(sector)
    assert len(result) == 1
    assert result[0].symbol == "XLK"

    # Sector top mutual funds
    result = sector_industry_service.get_sector_top_mutual_funds(sector)
    assert len(result) == 1
    assert result[0].symbol == "VFINX"

    # Sector industries
    result = sector_industry_service.get_sector_industries(sector)
    assert len(result) == 2
    assert "Software" in result

    # Sector research reports
    result = sector_industry_service.get_sector_research_reports(sector)
    assert len(result) == 1
    assert result[0].report_title == "Tech Sector Report"

    # All industries (with sector filter)
    result = sector_industry_service.get_all_industries(sector)
    assert len(result) == 3

    # All industries (no filter)
    result = sector_industry_service.get_all_industries()
    assert len(result) == 3

    # Industry overview
    result = sector_industry_service.get_industry_overview(industry)
    assert result.description == f"Overview for {industry}"

    # Industry top companies
    result = sector_industry_service.get_industry_top_companies(industry)
    assert len(result) == 1
    assert result[0].symbol == "MSFT"

    # Industry top growth companies
    result = sector_industry_service.get_industry_top_growth_companies(industry)
    assert len(result) == 1
    assert result[0].symbol == "NVDA"

    # Industry top performing companies
    result = sector_industry_service.get_industry_top_performing_companies(industry)
    assert len(result) == 1
    assert result[0].symbol == "GOOGL"

    # Verify all calls were made with correct arguments
    assert len(sector_industry_repository_spy.calls) == 14
