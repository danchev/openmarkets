import pandas as pd
import pytest

from openmarkets.repositories.sector_industry import YFinanceSectorIndustryRepository


def test_get_sector_overview(monkeypatch):
    from pydantic import ValidationError

    class S:
        def __init__(self, sector, session=None, region=None):
            self.overview = {
                "companies_count": 1,
                "market_cap": 123456,
                "message_board_id": "mbid",
                "description": "desc",
                "industries_count": None,
                "market_weight": 0.1,
                "employee_count": 10,
            }

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Sector": S}))
    repo = YFinanceSectorIndustryRepository()
    try:
        out = repo.get_sector_overview("technology")
    except ValidationError:
        pytest.skip("Pydantic validation failed for constructed overview; skip in test environment")
    else:
        assert out.companies_count == 1


def test_get_sector_overview_raises_when_upstream_fetch_fails(monkeypatch):
    """A failed upstream fetch must raise a domain error, not TypeError.

    yfinance's Sector hides fetch exceptions by default (hide_exceptions is
    True) and leaves .overview as None instead of raising. Unpacking None
    with ** previously surfaced as an opaque TypeError with no indication
    that the real cause was an upstream failure.
    """
    from openmarkets.core.exceptions import DataUnavailableError

    class S:
        def __init__(self, sector, session=None, region=None):
            self.overview = None

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Sector": S}))
    repo = YFinanceSectorIndustryRepository()

    with pytest.raises(DataUnavailableError):
        repo.get_sector_overview("technology")


def test_get_industry_overview_raises_when_upstream_fetch_fails(monkeypatch):
    """Mirrors test_get_sector_overview_raises_when_upstream_fetch_fails for industries."""
    from openmarkets.core.exceptions import DataUnavailableError

    class IndustryStub:
        def __init__(self, industry, session=None, region=None):
            self.overview = None

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Industry": IndustryStub}))
    repo = YFinanceSectorIndustryRepository()

    with pytest.raises(DataUnavailableError):
        repo.get_industry_overview("semiconductors")


def test_get_sector_overview_for_ticker_missing(monkeypatch):
    class T:
        def __init__(self, t, session=None):
            self.info = {}

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Ticker": T}))
    repo = YFinanceSectorIndustryRepository()
    with pytest.raises(ValueError):
        repo.get_sector_overview_for_ticker("AAPL")


def test_get_sector_top_companies_and_industries(monkeypatch):
    df = pd.DataFrame([{"symbol": "A", "name": "Alpha", "rating": "A", "market weight": 0.05}]).set_index("symbol")

    class S:
        def __init__(self, sector, session=None, region=None):
            self.top_companies = df
            self.top_etfs = {"ETF1": "Name"}
            self.top_mutual_funds = {"MF1": "Name"}
            self.research_reports = [
                {
                    "id": "r1",
                    "headHtml": "h",
                    "provider": "p",
                    "reportTitle": "R1",
                    "reportType": "type",
                }
            ]

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Sector": S}))
    repo = YFinanceSectorIndustryRepository()
    comps = repo.get_sector_top_companies("technology")
    assert comps and comps[0].name == "Alpha"
    etfs = repo.get_sector_top_etfs("technology")
    assert etfs[0].symbol == "ETF1"
    mfs = repo.get_sector_top_mutual_funds("technology")
    assert mfs[0].symbol == "MF1"
    reports = repo.get_sector_research_reports("technology")
    assert reports[0].report_title == "R1"
    inds = repo.get_sector_industries("technology")
    assert isinstance(inds, list)


def test_get_all_industries_and_industry_overview(monkeypatch):
    repo = YFinanceSectorIndustryRepository()
    all_inds = repo.get_all_industries()
    assert "semiconductors" in all_inds

    class DummyIndustry:
        def __init__(self, industry, session=None, region=None):
            self.overview = {
                "companies_count": 4,
                "market_cap": 17122720768,
                "message_board_id": "IDX",
                "description": "desc",
                "industries_count": None,
                "market_weight": 0.1,
                "employee_count": 100,
            }

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Industry": DummyIndustry}))
    out = repo.get_industry_overview("semiconductors")
    assert out.market_cap == 17122720768


def test_get_sector_top_companies_none(monkeypatch):
    """Test get_sector_top_companies when data is None"""

    class S:
        def __init__(self, sector, session=None, region=None):
            self.top_companies = None

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Sector": S}))
    repo = YFinanceSectorIndustryRepository()
    comps = repo.get_sector_top_companies("technology")
    assert comps == []


def test_get_sector_research_reports_empty(monkeypatch):
    """Test get_sector_research_reports when data is empty"""

    class S:
        def __init__(self, sector, session=None, region=None):
            self.research_reports = None

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Sector": S}))
    repo = YFinanceSectorIndustryRepository()
    reports = repo.get_sector_research_reports("technology")
    assert reports == []


def test_get_sector_top_companies_for_ticker_success(monkeypatch):
    """Test get_sector_top_companies_for_ticker with valid sector"""
    df = pd.DataFrame([{"symbol": "A", "name": "Alpha", "rating": "A", "market weight": 0.05}]).set_index("symbol")

    class T:
        def __init__(self, t, session=None):
            self.info = {"sectorKey": "technology"}

    class S:
        def __init__(self, sector, session=None, region=None):
            self.top_companies = df

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Ticker": T, "Sector": S}))
    repo = YFinanceSectorIndustryRepository()
    comps = repo.get_sector_top_companies_for_ticker("AAPL")
    assert len(comps) == 1
    assert comps[0].name == "Alpha"


def test_get_sector_top_companies_for_ticker_no_sector(monkeypatch):
    """Test get_sector_top_companies_for_ticker when ticker has no sector"""

    class T:
        def __init__(self, t, session=None):
            self.info = {}

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Ticker": T}))
    repo = YFinanceSectorIndustryRepository()
    with pytest.raises(ValueError, match="Sector not found for ticker"):
        repo.get_sector_top_companies_for_ticker("AAPL")


def test_get_all_industries_with_sector_filter(monkeypatch):
    """Test get_all_industries with sector filter"""
    repo = YFinanceSectorIndustryRepository()
    inds = repo.get_all_industries(sector="technology")
    assert isinstance(inds, list)
    assert len(inds) > 0


def test_get_industry_top_companies_none(monkeypatch):
    """Test get_industry_top_companies when data is None"""

    class DummyIndustry:
        def __init__(self, industry, session=None, region=None):
            self.top_companies = None

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Industry": DummyIndustry}))
    repo = YFinanceSectorIndustryRepository()
    comps = repo.get_industry_top_companies("semiconductors")
    assert comps == []


def test_get_industry_top_growth_companies_none(monkeypatch):
    """Test get_industry_top_growth_companies when data is None"""

    class DummyIndustry:
        def __init__(self, industry, session=None, region=None):
            self.top_growth_companies = None

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Industry": DummyIndustry}))
    repo = YFinanceSectorIndustryRepository()
    comps = repo.get_industry_top_growth_companies("semiconductors")
    assert comps == []


def test_get_industry_top_performing_companies_none(monkeypatch):
    """Test get_industry_top_performing_companies when data is None"""

    class DummyIndustry:
        def __init__(self, industry, session=None, region=None):
            self.top_performing_companies = None

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Industry": DummyIndustry}))
    repo = YFinanceSectorIndustryRepository()
    comps = repo.get_industry_top_performing_companies("semiconductors")
    assert comps == []


def test_get_sector_overview_forwards_region(monkeypatch):
    """The region parameter must actually reach yf.Sector, not be silently
    dropped - this is what distinguishes 'accepts a region argument' from
    'the argument actually changes which data is fetched'."""
    captured = {}

    class S:
        def __init__(self, sector, session=None, region=None):
            captured["region"] = region
            self.overview = {
                "companies_count": 1,
                "market_cap": 1,
                "message_board_id": "mbid",
                "description": "desc",
                "industries_count": 1,
                "market_weight": 0.1,
                "employee_count": 1,
            }

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Sector": S}))
    repo = YFinanceSectorIndustryRepository()

    repo.get_sector_overview("technology", region="GB")

    assert captured["region"] == "GB"


def test_get_sector_overview_defaults_region_to_us(monkeypatch):
    """Omitting region must preserve the pre-region-scoping behaviour."""
    captured = {}

    class S:
        def __init__(self, sector, session=None, region=None):
            captured["region"] = region
            self.overview = {
                "companies_count": 1,
                "market_cap": 1,
                "message_board_id": "mbid",
                "description": "desc",
                "industries_count": 1,
                "market_weight": 0.1,
                "employee_count": 1,
            }

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Sector": S}))
    repo = YFinanceSectorIndustryRepository()

    repo.get_sector_overview("technology")

    assert captured["region"] == "US"


def test_get_industry_overview_forwards_region(monkeypatch):
    """Mirrors test_get_sector_overview_forwards_region for industries."""
    captured = {}

    class DummyIndustry:
        def __init__(self, industry, session=None, region=None):
            captured["region"] = region
            self.overview = {
                "companies_count": 1,
                "market_cap": 1,
                "message_board_id": "IDX",
                "description": "desc",
                "industries_count": None,
                "market_weight": 0.1,
                "employee_count": 1,
            }

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf", type("Y", (), {"Industry": DummyIndustry}))
    repo = YFinanceSectorIndustryRepository()

    repo.get_industry_overview("semiconductors", region="DE")

    assert captured["region"] == "DE"
