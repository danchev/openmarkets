"""
Unit tests for get_all_industries in sector_industry.py
"""

from openmarkets.schemas.sector_industry import SECTOR_INDUSTRY_MAPPING, SectorEnum
from openmarkets.services.yfinance.sector_industry import fetch_all_industries


def test_get_all_industries_all():
    # Should return all unique industries sorted
    industries = fetch_all_industries()
    expected = sorted({industry for inds in SECTOR_INDUSTRY_MAPPING.values() for industry in inds})
    assert industries == expected


def test_get_all_industries_sector():
    # Should return only industries for the given sector
    for sector in SectorEnum:
        industries = fetch_all_industries(sector)
        expected = sorted(SECTOR_INDUSTRY_MAPPING.get(sector.value, []))
        assert industries == expected


def test_get_all_industries_invalid_sector():
    # Should return empty list for sector not in mapping
    class Dummy:
        value = "not-a-sector"

    industries = fetch_all_industries(Dummy())
    assert industries == []
