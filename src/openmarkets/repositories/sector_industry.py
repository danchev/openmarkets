"""Repository layer for sector and industry data operations.

Provides abstractions and implementations for fetching sector overviews,
industry information, top companies, and related sector/industry analytics.
"""

from abc import ABC, abstractmethod

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.schemas.sector_industry import (
    SECTOR_INDUSTRY_MAPPING,
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


class ISectorIndustryRepository(ABC):
    """Abstract interface for sector and industry data repositories."""

    @abstractmethod
    def get_sector_overview(self, sector: str, session: Session | None = None) -> SectorOverview:
        pass

    @abstractmethod
    def get_sector_overview_for_ticker(self, ticker: str, session: Session | None = None) -> SectorOverview:
        pass

    @abstractmethod
    def get_sector_top_companies(self, sector: str, session: Session | None = None) -> list[SectorTopCompaniesEntry]:
        pass

    @abstractmethod
    def get_sector_top_companies_for_ticker(
        self, ticker: str, session: Session | None = None
    ) -> list[SectorTopCompaniesEntry]:
        pass

    @abstractmethod
    def get_sector_top_etfs(self, sector: str, session: Session | None = None) -> list[SectorTopETFsEntry]:
        pass

    @abstractmethod
    def get_sector_top_mutual_funds(
        self, sector: str, session: Session | None = None
    ) -> list[SectorTopMutualFundsEntry]:
        pass

    @abstractmethod
    def get_sector_industries(self, sector: str, session: Session | None = None) -> list[str]:
        pass

    @abstractmethod
    def get_sector_research_reports(
        self, sector: str, session: Session | None = None
    ) -> list[IndustryResearchReportEntry]:
        pass

    @abstractmethod
    def get_all_industries(self, sector: str | None = None, session: Session | None = None) -> list[str]:
        pass

    @abstractmethod
    def get_industry_overview(self, industry: str, session: Session | None = None) -> IndustryOverview:
        pass

    @abstractmethod
    def get_industry_top_companies(
        self, industry: str, session: Session | None = None
    ) -> list[IndustryTopCompaniesEntry]:
        pass

    @abstractmethod
    def get_industry_top_growth_companies(
        self, industry: str, session: Session | None = None
    ) -> list[IndustryTopGrowthCompaniesEntry]:
        pass

    @abstractmethod
    def get_industry_top_performing_companies(
        self, industry: str, session: Session | None = None
    ) -> list[IndustryTopPerformingCompaniesEntry]:
        pass


class YFinanceSectorIndustryRepository(ISectorIndustryRepository):
    """Repository for accessing sector and industry data from yfinance."""

    def get_sector_overview(self, sector: str, session: Session | None = None) -> SectorOverview:
        """Retrieve sector overview.

        Args:
            sector: Sector identifier.
            session: Optional HTTP session for request handling.

        Returns:
            Sector overview data.
        """
        sector_obj = yf.Sector(sector, session=session)
        data = sector_obj.overview
        return SectorOverview(**data)

    def get_sector_overview_for_ticker(self, ticker: str, session: Session | None = None) -> SectorOverview:
        """Retrieve sector overview for a given ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Sector overview data.

        Raises:
            ValueError: If sector not found for ticker.
        """
        stock = yf.Ticker(ticker, session=session)
        sector = stock.info.get("sectorKey")
        if sector is None:
            raise ValueError(f"Sector not found for ticker: {ticker}")
        return self.get_sector_overview(sector, session=session)

    def get_sector_top_companies(self, sector: str, session: Session | None = None) -> list[SectorTopCompaniesEntry]:
        """Retrieve top companies for a sector.

        Args:
            sector: Sector identifier.
            session: Optional HTTP session for request handling.

        Returns:
            List of sector top companies.
        """
        sector_obj = yf.Sector(sector, session=session)
        data = sector_obj.top_companies
        if data is None:
            return []
        reset_data = data.reset_index()
        return [SectorTopCompaniesEntry(**row.to_dict()) for _, row in reset_data.iterrows()]

    def get_sector_top_companies_for_ticker(
        self, ticker: str, session: Session | None = None
    ) -> list[SectorTopCompaniesEntry]:
        """Retrieve sector top companies for a given ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of sector top companies.

        Raises:
            ValueError: If sector not found for ticker.
        """
        stock = yf.Ticker(ticker, session=session)
        sector = stock.info.get("sectorKey")
        if sector is None:
            raise ValueError(f"Sector not found for ticker: {ticker}")
        return self.get_sector_top_companies(sector, session=session)

    def get_sector_top_etfs(self, sector: str, session: Session | None = None) -> list[SectorTopETFsEntry]:
        """Retrieve top ETFs for a sector.

        Args:
            sector: Sector identifier.
            session: Optional HTTP session for request handling.

        Returns:
            List of sector top ETFs.
        """
        sector_obj = yf.Sector(sector, session=session)
        data = sector_obj.top_etfs
        return [SectorTopETFsEntry(symbol=k, name=v) for k, v in data.items()]

    def get_sector_top_mutual_funds(
        self, sector: str, session: Session | None = None
    ) -> list[SectorTopMutualFundsEntry]:
        """Retrieve top mutual funds for a sector.

        Args:
            sector: Sector identifier.
            session: Optional HTTP session for request handling.

        Returns:
            List of sector top mutual funds.
        """
        sector_obj = yf.Sector(sector, session=session)
        data = sector_obj.top_mutual_funds
        return [SectorTopMutualFundsEntry(symbol=k, name=v) for k, v in data.items()]

    def get_sector_industries(self, sector: str, session: Session | None = None) -> list[str]:
        """Retrieve industries within a sector.

        Args:
            sector: Sector identifier.
            session: Optional HTTP session for request handling.

        Returns:
            List of industry names.
        """
        return SECTOR_INDUSTRY_MAPPING.get(sector, [])

    def get_sector_research_reports(
        self, sector: str, session: Session | None = None
    ) -> list[IndustryResearchReportEntry]:
        """Retrieve research reports for a sector.

        Args:
            sector: Sector identifier.
            session: Optional HTTP session for request handling.

        Returns:
            List of research report entries.
        """
        sector_obj = yf.Sector(sector, session=session)
        data = sector_obj.research_reports
        if not data:
            return []
        return [IndustryResearchReportEntry(**entry) for entry in data]

    def get_all_industries(self, sector: str | None = None, session: Session | None = None) -> list[str]:
        """Retrieve all industries, optionally filtered by sector.

        Args:
            sector: Optional sector filter.
            session: Optional HTTP session for request handling.

        Returns:
            Sorted list of industry names.
        """
        if sector is not None:
            return sorted(SECTOR_INDUSTRY_MAPPING.get(sector, []))
        return sorted({industry for industries in SECTOR_INDUSTRY_MAPPING.values() for industry in industries})

    def get_industry_overview(self, industry: str, session: Session | None = None) -> IndustryOverview:
        """Retrieve industry overview.

        Args:
            industry: Industry identifier.
            session: Optional HTTP session for request handling.

        Returns:
            Industry overview data.
        """
        industry_obj = yf.Industry(industry, session=session)
        data = industry_obj.overview
        return IndustryOverview(**data)

    def get_industry_top_companies(
        self, industry: str, session: Session | None = None
    ) -> list[IndustryTopCompaniesEntry]:
        """Retrieve top companies for an industry.

        Args:
            industry: Industry identifier.
            session: Optional HTTP session for request handling.

        Returns:
            List of industry top companies.
        """
        industry_obj = yf.Industry(industry, session=session)
        data = industry_obj.top_companies
        if data is None:
            return []
        reset_data = data.reset_index()
        return [IndustryTopCompaniesEntry(**row.to_dict()) for _, row in reset_data.iterrows()]

    def get_industry_top_growth_companies(
        self, industry: str, session: Session | None = None
    ) -> list[IndustryTopGrowthCompaniesEntry]:
        """Retrieve top growth companies for an industry.

        Args:
            industry: Industry identifier.
            session: Optional HTTP session for request handling.

        Returns:
            List of industry top growth companies.
        """
        industry_obj = yf.Industry(industry, session=session)
        data = industry_obj.top_growth_companies
        if data is None:
            return []
        reset_data = data.reset_index()
        return [IndustryTopGrowthCompaniesEntry(**row.to_dict()) for _, row in reset_data.iterrows()]

    def get_industry_top_performing_companies(
        self, industry: str, session: Session | None = None
    ) -> list[IndustryTopPerformingCompaniesEntry]:
        """Retrieve top performing companies for an industry.

        Args:
            industry: Industry identifier.
            session: Optional HTTP session for request handling.

        Returns:
            List of industry top performing companies.
        """
        industry_obj = yf.Industry(industry, session=session)
        data = industry_obj.top_performing_companies
        if data is None:
            return []
        reset_data = data.reset_index()
        return [IndustryTopPerformingCompaniesEntry(**row.to_dict()) for _, row in reset_data.iterrows()]
