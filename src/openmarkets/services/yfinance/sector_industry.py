from typing import List, Optional

import yfinance as yf

from openmarkets.schemas.sector_industry import (
    SECTOR_INDUSTRY_MAPPING,
    IndustryOverview,
    IndustryResearchReportEntry,
    IndustryTopCompaniesEntry,
    IndustryTopGrowthCompaniesEntry,
    SectorEnum,
    SectorOverview,
    SectorTopCompaniesEntry,
    SectorTopETFsEntry,
    SectorTopMutualFundsEntry,
)


def get_sector_overview(sector: SectorEnum) -> SectorOverview:
    """Fetches overview information for a given sector.

    Args:
        sector: The sector name (e.g., "technology").

    Returns:
        SectorOverview: Overview data for the sector.

    Raises:
        ValueError: If the sector is not recognized.
    """
    print(f"Fetching overview for sector: {sector}")
    data = yf.Sector(sector.value).overview
    return SectorOverview(**data)


def get_sector_overview_for_ticker(ticker: str) -> SectorOverview:
    """Fetches overview information for the sector of a given ticker.

    Args:
        ticker: The stock ticker symbol (e.g., "MSFT").

    Returns:
        SectorOverview: Overview data for the sector of the ticker.

    Raises:
        ValueError: If the ticker or sector is not recognized.
    """
    stock = yf.Ticker(ticker)
    sector = stock.info.get("sectorKey")
    return get_sector_overview(SectorEnum[sector.upper()])


def get_sector_top_companies(sector: SectorEnum) -> List[SectorTopCompaniesEntry]:
    """Fetches top companies for a given sector.

    Args:
        sector: The sector name.

    Returns:
        List of SectorTopCompaniesEntry.
    """
    data = yf.Sector(sector.value).top_companies
    return [SectorTopCompaniesEntry(**row.to_dict()) for _, row in data.reset_index().iterrows()]


def get_sector_top_companies_for_ticker(ticker: str) -> List[SectorTopCompaniesEntry]:
    """Fetches top companies for the sector of a given ticker.

    Args:
        ticker: The stock ticker symbol (e.g., "MSFT").

    Returns:
        List of SectorTopCompaniesEntry.
    """
    stock = yf.Ticker(ticker)
    sector = stock.info.get("sectorKey")
    return get_sector_top_companies(SectorEnum[sector.upper()])


def get_sector_top_etfs(sector: SectorEnum) -> List[SectorTopETFsEntry]:
    """Fetches top ETFs for a given sector.

    Args:
        sector: The sector name.

    Returns:
        List of SectorTopETFsEntry.
    """
    data = yf.Sector(sector.value).top_etfs
    return [SectorTopETFsEntry(symbol=k, name=v) for k, v in data.items()]


def get_sector_top_mutual_funds(sector: SectorEnum) -> List[SectorTopMutualFundsEntry]:
    """Fetches top mutual funds for a given sector.

    Args:
        sector: The sector name.

    Returns:
        List of SectorTopMutualFundsEntry.
    """
    data = yf.Sector(sector.value).top_mutual_funds
    return [SectorTopMutualFundsEntry(symbol=k, name=v) for k, v in data.items()]


def get_sector_industries(sector: SectorEnum) -> List[str]:
    """Returns the list of industries for a given sector.

    Args:
        sector: The sector name.

    Returns:
        List of industry names.
    """
    return SECTOR_INDUSTRY_MAPPING.get(sector.value, [])


def get_sector_research_reports(sector: SectorEnum) -> List[IndustryResearchReportEntry]:
    """Fetches research reports for a given sector.

    Args:
        sector: The sector name.

    Returns:
        List of IndustryResearchReportEntry.

    Raises:
        ValueError: If the sector is not recognized or no reports are found.
    """
    data = yf.Sector(sector.value).research_reports
    if not data:
        return []
    return [IndustryResearchReportEntry(**entry) for entry in data]


def get_all_industries(sector: Optional[SectorEnum] = None) -> List[str]:
    """Returns a list of industries.

    If sector is provided, returns industries for that sector only.
    If sector is None, returns all industries across all sectors.

    Args:
        sector: Optional; the sector to filter industries by.

    Returns:
        List of industry names.
    """
    if sector is not None:
        return sorted(SECTOR_INDUSTRY_MAPPING.get(sector.value, []))
    return sorted({industry for industries in SECTOR_INDUSTRY_MAPPING.values() for industry in industries})


def get_industry_overview(industry: str) -> IndustryOverview:
    """Fetches overview information for a given industry.

    Args:
        industry: The industry name (e.g., "aluminum").

    Returns:
        IndustryOverview: Overview data for the industry.
    """
    data = yf.Industry(industry).overview
    return IndustryOverview(**data)


def get_industry_top_companies(industry: str) -> List[IndustryTopCompaniesEntry]:
    """Fetches top companies for a given industry.

    Args:
        industry: The industry name.
    Returns:
        List of IndustryTopCompaniesEntry.
    """
    data = yf.Industry(industry).top_companies
    return [IndustryTopCompaniesEntry(**row.to_dict()) for _, row in data.reset_index().iterrows()]


def get_industry_top_growth_companies(industry: str) -> List[IndustryTopGrowthCompaniesEntry]:
    """Fetches top growth companies for a given industry.

    Args:
        industry: The industry name.
    Returns:
        List of IndustryTopGrowthCompaniesEntry.
    """
    data = yf.Industry(industry).top_growth_companies
    return [IndustryTopGrowthCompaniesEntry(**row.to_dict()) for _, row in data.reset_index().iterrows()]
