"""Service layer for sector and industry data operations.

Provides business logic for retrieving sector overviews, industry information,
top companies, ETFs, mutual funds, and research reports. Acts as an intermediary
between the MCP tools layer and repository layer.
"""

from typing import Annotated

from openmarkets.core.types import Region, Ticker
from openmarkets.repositories.sector_industry import DEFAULT_REGION, YFinanceSectorIndustryRepository
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
from openmarkets.services.utils import ToolRegistrationMixin, tool


class SectorIndustryService(ToolRegistrationMixin):
    """
    Service layer for sector and industry-related business logic.
    Provides methods to retrieve sector and industry overviews, top companies, ETFs, mutual funds, and research reports.
    """

    def __init__(self, repository: YFinanceSectorIndustryRepository | None = None):
        """Initialize the SectorIndustryService.

        Args:
            repository: Repository instance for data access. Defaults to YFinanceSectorIndustryRepository.
        """
        self.repository = repository or YFinanceSectorIndustryRepository()

    @tool
    def get_sector_overview(
        self, sector: Annotated[str, SectorEnum.__members__], region: Region = DEFAULT_REGION
    ) -> SectorOverview:
        """
        Retrieve overview information for a specific sector.

        Args:
            sector (str): The name of the sector.
            region (str): ISO 3166-1 alpha-2 country code scoping the data. Defaults to 'US'.
        Returns:
            SectorOverview: Overview data for the sector.
        """
        return self.repository.get_sector_overview(sector, region=region)

    @tool
    def get_sector_overview_for_ticker(self, ticker: Ticker, region: Region = DEFAULT_REGION) -> SectorOverview:
        """
        Retrieve overview information for a specific sector based on a stock ticker.

        Args:
            ticker (str): The stock ticker symbol.
            region (str): ISO 3166-1 alpha-2 country code scoping the data. Defaults to 'US'.
        Returns:
            SectorOverview: Overview data for the sector associated with the ticker.
        """
        return self.repository.get_sector_overview_for_ticker(ticker, region=region)

    @tool
    def get_sector_top_companies(
        self, sector: Annotated[str, SectorEnum.__members__], region: Region = DEFAULT_REGION
    ) -> list[SectorTopCompaniesEntry]:
        """
        Retrieve a list of top companies within a specific sector.

        Args:
            sector (str): The name of the sector.
            region (str): ISO 3166-1 alpha-2 country code scoping the data. Defaults to 'US'.
        Returns:
            list[SectorTopCompaniesEntry]: A list of top companies in the sector.
        """
        return self.repository.get_sector_top_companies(sector, region=region)

    @tool
    def get_sector_top_companies_for_ticker(
        self, ticker: Ticker, region: Region = DEFAULT_REGION
    ) -> list[SectorTopCompaniesEntry]:
        """
        Retrieve a list of top companies within a specific sector based on a stock ticker.

        Args:
            ticker (str): The stock ticker symbol.
            region (str): ISO 3166-1 alpha-2 country code scoping the data. Defaults to 'US'.
        Returns:
            list[SectorTopCompaniesEntry]: A list of top companies in the sector associated with the ticker.
        """
        return self.repository.get_sector_top_companies_for_ticker(ticker, region=region)

    @tool
    def get_sector_top_etfs(
        self, sector: Annotated[str, SectorEnum.__members__], region: Region = DEFAULT_REGION
    ) -> list[SectorTopETFsEntry]:
        """
        Retrieve a list of top ETFs within a specific sector.

        Args:
            sector (str): The name of the sector.
            region (str): ISO 3166-1 alpha-2 country code scoping the data. Defaults to 'US'.
        Returns:
            list[SectorTopETFsEntry]: A list of top ETFs in the sector.
        """
        return self.repository.get_sector_top_etfs(sector, region=region)

    @tool
    def get_sector_top_mutual_funds(
        self, sector: Annotated[str, SectorEnum.__members__], region: Region = DEFAULT_REGION
    ) -> list[SectorTopMutualFundsEntry]:
        """
        Retrieve a list of top mutual funds within a specific sector.

        Args:
            sector (str): The name of the sector.
            region (str): ISO 3166-1 alpha-2 country code scoping the data. Defaults to 'US'.
        Returns:
            list[SectorTopMutualFundsEntry]: A list of top mutual funds in the sector.
        """
        return self.repository.get_sector_top_mutual_funds(sector, region=region)

    @tool
    def get_sector_industries(self, sector: Annotated[str, SectorEnum.__members__]) -> list[str]:
        """
        Retrieve a list of industries within a specific sector.

        Backed by a static local mapping rather than a region-scoped
        upstream call, so this tool takes no region parameter.

        Args:
            sector (str): The name of the sector.
        Returns:
            list[str]: A list of industries in the sector.
        """
        return self.repository.get_sector_industries(sector)

    @tool
    def get_sector_research_reports(
        self, sector: Annotated[str, SectorEnum.__members__], region: Region = DEFAULT_REGION
    ) -> list[IndustryResearchReportEntry]:
        """
        Retrieve a list of research reports within a specific sector.

        Args:
            sector (str): The name of the sector.
            region (str): ISO 3166-1 alpha-2 country code scoping the data. Defaults to 'US'.
        Returns:
            list[IndustryResearchReportEntry]: A list of research reports in the sector.
        """
        return self.repository.get_sector_research_reports(sector, region=region)

    @tool
    def get_all_industries(self, sector: Annotated[str | None, "The name of the sector."] = None) -> list[str]:
        """
        Retrieve a list of all industries, optionally filtered by sector.

        Backed by a static local mapping rather than a region-scoped
        upstream call, so this tool takes no region parameter.

        Args:
            sector (str | None): The name of the sector to filter by, or None to retrieve all industries.
        Returns:
            list[str]: A list of all industries, or industries in the specified sector.
        """
        return self.repository.get_all_industries(sector)

    @tool
    def get_industry_overview(self, industry: str, region: Region = DEFAULT_REGION) -> IndustryOverview:
        """
        Retrieve an overview of a specific industry.

        Args:
            industry (str): The name of the industry.
            region (str): ISO 3166-1 alpha-2 country code scoping the data. Defaults to 'US'.
        Returns:
            IndustryOverview: An overview of the specified industry.
        """
        return self.repository.get_industry_overview(industry, region=region)

    @tool
    def get_industry_top_companies(
        self, industry: str, region: Region = DEFAULT_REGION
    ) -> list[IndustryTopCompaniesEntry]:
        """
        Retrieve a list of top companies within a specific industry.

        Args:
            industry (str): The name of the industry.
            region (str): ISO 3166-1 alpha-2 country code scoping the data. Defaults to 'US'.
        Returns:
            list[IndustryTopCompaniesEntry]: A list of top companies in the industry.
        """
        return self.repository.get_industry_top_companies(industry, region=region)

    @tool
    def get_industry_top_growth_companies(
        self, industry: str, region: Region = DEFAULT_REGION
    ) -> list[IndustryTopGrowthCompaniesEntry]:
        """
        Retrieve a list of top growth companies within a specific industry.

        Args:
            industry (str): The name of the industry.
            region (str): ISO 3166-1 alpha-2 country code scoping the data. Defaults to 'US'.
        Returns:
            list[IndustryTopGrowthCompaniesEntry]: A list of top growth companies in the industry.
        """
        return self.repository.get_industry_top_growth_companies(industry, region=region)

    @tool
    def get_industry_top_performing_companies(
        self, industry: str, region: Region = DEFAULT_REGION
    ) -> list[IndustryTopPerformingCompaniesEntry]:
        """
        Retrieve a list of top performing companies within a specific industry.

        Args:
            industry (str): The name of the industry.
            region (str): ISO 3166-1 alpha-2 country code scoping the data. Defaults to 'US'.
        Returns:
            list[IndustryTopPerformingCompaniesEntry]: A list of top growth companies in the industry.
        """
        return self.repository.get_industry_top_performing_companies(industry, region=region)


sector_industry_service = SectorIndustryService()
