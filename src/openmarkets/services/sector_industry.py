from typing import Annotated

from openmarkets.repositories.sector_industry import ISectorIndustryRepository, YFinanceSectorIndustryRepository
from openmarkets.schemas.sector_industry import (
    IndustryOverview,
    IndustryResearchReportEntry,
    IndustryTopCompaniesEntry,
    IndustryTopGrowthCompaniesEntry,
    IndustryTopPerformingCompaniesEntry,
    SectorEnum,
    SectorOverview,
    SectorTopCompaniesEntry,
    SectorTopETFsEntry,
    SectorTopMutualFundsEntry,
)
from openmarkets.services.utils import ToolRegistrationMixin


class SectorIndustryService(ToolRegistrationMixin):
    """
    Service layer for sector and industry-related business logic.
    Provides methods to retrieve sector and industry overviews, top companies, ETFs, mutual funds, and research reports.
    """

    def __init__(self, repository: ISectorIndustryRepository | None = None):
        """
        Initialize the SectorIndustryService with a repository dependency.

        Args:
            repository (ISectorIndustryRepository): The repository instance for data access.
        """
        self.repository = repository or YFinanceSectorIndustryRepository()

    def get_sector_overview(self, sector: Annotated[str, SectorEnum.__members__]) -> SectorOverview:
        """
        Retrieve overview information for a specific sector.

        Args:
            sector (str): The name of the sector.
        Returns:
            SectorOverview: Overview data for the sector.
        """
        return self.repository.get_sector_overview(sector)

    def get_sector_overview_for_ticker(self, ticker: str) -> SectorOverview:
        """
        Retrieve overview information for a specific sector based on a stock ticker.

        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            SectorOverview: Overview data for the sector associated with the ticker.
        """
        return self.repository.get_sector_overview_for_ticker(ticker)

    def get_sector_top_companies(self, sector: Annotated[str, SectorEnum.__members__]) -> list[SectorTopCompaniesEntry]:
        """
        Retrieve a list of top companies within a specific sector.

        Args:
            sector (str): The name of the sector.
        Returns:
            list[SectorTopCompaniesEntry]: A list of top companies in the sector.
        """
        return self.repository.get_sector_top_companies(sector)

    def get_sector_top_companies_for_ticker(self, ticker: str) -> list[SectorTopCompaniesEntry]:
        """
        Retrieve a list of top companies within a specific sector based on a stock ticker.

        Args:
            ticker (str): The stock ticker symbol.
        Returns:
            list[SectorTopCompaniesEntry]: A list of top companies in the sector associated with the ticker.
        """
        return self.repository.get_sector_top_companies_for_ticker(ticker)

    def get_sector_top_etfs(self, sector: Annotated[str, SectorEnum.__members__]) -> list[SectorTopETFsEntry]:
        """
        Retrieve a list of top ETFs within a specific sector.

        Args:
            sector (str): The name of the sector.
        Returns:
            list[SectorTopETFsEntry]: A list of top ETFs in the sector.
        """
        return self.repository.get_sector_top_etfs(sector)

    def get_sector_top_mutual_funds(
        self, sector: Annotated[str, SectorEnum.__members__]
    ) -> list[SectorTopMutualFundsEntry]:
        """
        Retrieve a list of top mutual funds within a specific sector.

        Args:
            sector (str): The name of the sector.
        Returns:
            list[SectorTopMutualFundsEntry]: A list of top mutual funds in the sector.
        """
        return self.repository.get_sector_top_mutual_funds(sector)

    def get_sector_industries(self, sector: Annotated[str, SectorEnum.__members__]) -> list[str]:
        """
        Retrieve a list of industries within a specific sector.

        Args:
            sector (str): The name of the sector.
        Returns:
            list[str]: A list of industries in the sector.
        """
        return self.repository.get_sector_industries(sector)

    def get_sector_research_reports(
        self, sector: Annotated[str, SectorEnum.__members__]
    ) -> list[IndustryResearchReportEntry]:
        """
        Retrieve a list of research reports within a specific sector.

        Args:
            sector (str): The name of the sector.
        Returns:
            list[IndustryResearchReportEntry]: A list of research reports in the sector.
        """
        return self.repository.get_sector_research_reports(sector)

    def get_all_industries(self, sector: Annotated[str | None, "The name of the sector."] = None) -> list[str]:
        """
        Retrieve a list of all industries, optionally filtered by sector.

        Args:
            sector (str | None): The name of the sector to filter by, or None to retrieve all industries.
        Returns:
            list[str]: A list of all industries, or industries in the specified sector.
        """
        return self.repository.get_all_industries(sector)

    def get_industry_overview(self, industry: str) -> IndustryOverview:
        """
        Retrieve an overview of a specific industry.

        Args:
            industry (str): The name of the industry.
        Returns:
            IndustryOverview: An overview of the specified industry.
        """
        return self.repository.get_industry_overview(industry)

    def get_industry_top_companies(self, industry: str) -> list[IndustryTopCompaniesEntry]:
        """
        Retrieve a list of top companies within a specific industry.

        Args:
            industry (str): The name of the industry.
        Returns:
            list[IndustryTopCompaniesEntry]: A list of top companies in the industry.
        """
        return self.repository.get_industry_top_companies(industry)

    def get_industry_top_growth_companies(self, industry: str) -> list[IndustryTopGrowthCompaniesEntry]:
        """
        Retrieve a list of top growth companies within a specific industry.

        Args:
            industry (str): The name of the industry.
        Returns:
            list[IndustryTopGrowthCompaniesEntry]: A list of top growth companies in the industry.
        """
        return self.repository.get_industry_top_growth_companies(industry)

    def get_industry_top_performing_companies(self, industry: str) -> list[IndustryTopPerformingCompaniesEntry]:
        """
        Retrieve a list of top performing companies within a specific industry.

        Args:
            industry (str): The name of the industry.
        Returns:
            list[IndustryTopPerformingCompaniesEntry]: A list of top growth companies in the industry.
        """
        return self.repository.get_industry_top_performing_companies(industry)


sector_industry_service = SectorIndustryService()
