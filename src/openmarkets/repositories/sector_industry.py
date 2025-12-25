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
    def get_sector_overview(self, sector: str, session: Session | None = None) -> SectorOverview:
        data = yf.Sector(sector, session=session).overview
        return SectorOverview(**data)

    def get_sector_overview_for_ticker(self, ticker: str, session: Session | None = None) -> SectorOverview:
        stock = yf.Ticker(ticker, session=session)
        sector = stock.info.get("sectorKey")
        if sector is None:
            raise ValueError(f"Sector not found for ticker: {ticker}")
        return self.get_sector_overview(sector, session=session)

    def get_sector_top_companies(self, sector: str, session: Session | None = None) -> list[SectorTopCompaniesEntry]:
        data = yf.Sector(sector, session=session).top_companies
        if data is None:
            return []
        return [SectorTopCompaniesEntry(**row.to_dict()) for _, row in data.reset_index().iterrows()]

    def get_sector_top_companies_for_ticker(
        self, ticker: str, session: Session | None = None
    ) -> list[SectorTopCompaniesEntry]:
        stock = yf.Ticker(ticker, session=session)
        sector = stock.info.get("sectorKey")
        if sector is None:
            raise ValueError(f"Sector not found for ticker: {ticker}")
        return self.get_sector_top_companies(sector, session=session)

    def get_sector_top_etfs(self, sector: str, session: Session | None = None) -> list[SectorTopETFsEntry]:
        data = yf.Sector(sector, session=session).top_etfs
        return [SectorTopETFsEntry(symbol=k, name=v) for k, v in data.items()]

    def get_sector_top_mutual_funds(
        self, sector: str, session: Session | None = None
    ) -> list[SectorTopMutualFundsEntry]:
        data = yf.Sector(sector, session=session).top_mutual_funds
        return [SectorTopMutualFundsEntry(symbol=k, name=v) for k, v in data.items()]

    def get_sector_industries(self, sector: str, session: Session | None = None) -> list[str]:
        return SECTOR_INDUSTRY_MAPPING.get(sector, [])

    def get_sector_research_reports(
        self, sector: str, session: Session | None = None
    ) -> list[IndustryResearchReportEntry]:
        data = yf.Sector(sector, session=session).research_reports
        if not data:
            return []
        return [IndustryResearchReportEntry(**entry) for entry in data]

    def get_all_industries(self, sector: str | None = None, session: Session | None = None) -> list[str]:
        if sector is not None:
            return sorted(SECTOR_INDUSTRY_MAPPING.get(sector, []))
        return sorted({industry for industries in SECTOR_INDUSTRY_MAPPING.values() for industry in industries})

    def get_industry_overview(self, industry: str, session: Session | None = None) -> IndustryOverview:
        data = yf.Industry(industry, session=session).overview
        return IndustryOverview(**data)

    def get_industry_top_companies(
        self, industry: str, session: Session | None = None
    ) -> list[IndustryTopCompaniesEntry]:
        data = yf.Industry(industry, session=session).top_companies
        if data is None:
            return []
        return [IndustryTopCompaniesEntry(**row.to_dict()) for _, row in data.reset_index().iterrows()]

    def get_industry_top_growth_companies(
        self, industry: str, session: Session | None = None
    ) -> list[IndustryTopGrowthCompaniesEntry]:
        data = yf.Industry(industry, session=session).top_growth_companies
        if data is None:
            return []
        return [IndustryTopGrowthCompaniesEntry(**row.to_dict()) for _, row in data.reset_index().iterrows()]

    def get_industry_top_performing_companies(
        self, industry: str, session: Session | None = None
    ) -> list[IndustryTopPerformingCompaniesEntry]:
        data = yf.Industry(industry, session=session).top_performing_companies
        if data is None:
            return []
        return [IndustryTopPerformingCompaniesEntry(**row.to_dict()) for _, row in data.reset_index().iterrows()]
