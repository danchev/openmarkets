from types import SimpleNamespace

import pytest

from openmarkets.repositories.sector_industry import YFinanceSectorIndustryRepository
from openmarkets.schemas.sector_industry import SECTOR_INDUSTRY_MAPPING


class _FakeDF:
    def __init__(self, rows):
        self._rows = rows

    def reset_index(self):
        return self

    def iterrows(self):
        for i, row in enumerate(self._rows):
            yield i, row


class _RowLike:
    def __init__(self, data):
        self._data = data

    def to_dict(self):
        return self._data


def test_get_sector_overview_for_ticker_missing_sector(monkeypatch):
    repo = YFinanceSectorIndustryRepository()

    class FakeTicker:
        info = {}

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf.Ticker", lambda ticker, session=None: FakeTicker())

    with pytest.raises(ValueError):
        repo.get_sector_overview_for_ticker("FOO")


def test_get_sector_overview(monkeypatch):
    repo = YFinanceSectorIndustryRepository()

    fake_overview = {
        "companies_count": 2,
        "market_cap": 1000,
        "message_board_id": "mb",
        "description": "desc",
        "industries_count": 1,
        "market_weight": 0.5,
        "employee_count": 10,
    }

    monkeypatch.setattr(
        "openmarkets.repositories.sector_industry.yf.Sector",
        lambda sector, session=None: SimpleNamespace(overview=fake_overview),
    )

    res = repo.get_sector_overview("technology")
    assert res.companies_count == 2
    assert res.market_cap == 1000


def test_get_sector_top_companies_none(monkeypatch):
    repo = YFinanceSectorIndustryRepository()

    monkeypatch.setattr(
        "openmarkets.repositories.sector_industry.yf.Sector",
        lambda sector, session=None: SimpleNamespace(top_companies=None),
    )

    res = repo.get_sector_top_companies("technology")
    assert res == []


def test_get_sector_top_companies_from_df(monkeypatch):
    repo = YFinanceSectorIndustryRepository()

    row = _RowLike({"symbol": "A", "name": "Alpha", "rating": "R", "market weight": 0.1})
    df = _FakeDF([row])

    monkeypatch.setattr(
        "openmarkets.repositories.sector_industry.yf.Sector",
        lambda sector, session=None: SimpleNamespace(top_companies=df),
    )

    res = repo.get_sector_top_companies("technology")
    assert len(res) == 1
    assert res[0].symbol == "A"


def test_get_sector_top_companies_for_ticker_missing(monkeypatch):
    repo = YFinanceSectorIndustryRepository()

    class FakeTicker:
        info = {}

    monkeypatch.setattr("openmarkets.repositories.sector_industry.yf.Ticker", lambda ticker, session=None: FakeTicker())

    with pytest.raises(ValueError):
        repo.get_sector_top_companies_for_ticker("FOO")


def test_get_sector_top_etfs_and_mutuals(monkeypatch):
    repo = YFinanceSectorIndustryRepository()

    monkeypatch.setattr(
        "openmarkets.repositories.sector_industry.yf.Sector",
        lambda sector, session=None: SimpleNamespace(top_etfs={"ETF1": "E1"}, top_mutual_funds={"MF1": "M1"}),
    )

    etfs = repo.get_sector_top_etfs("tech")
    mfs = repo.get_sector_top_mutual_funds("tech")

    assert len(etfs) == 1
    assert etfs[0].symbol == "ETF1"
    assert len(mfs) == 1
    assert mfs[0].symbol == "MF1"


def test_get_sector_industries_and_all_industries():
    repo = YFinanceSectorIndustryRepository()

    # Sector mapping exists
    sector = next(iter(SECTOR_INDUSTRY_MAPPING))
    res = repo.get_sector_industries(sector)
    assert isinstance(res, list)

    # All industries
    all_ind = repo.get_all_industries()
    assert isinstance(all_ind, list)
    assert all(i in sum(SECTOR_INDUSTRY_MAPPING.values(), []) for i in all_ind)


def test_get_sector_research_reports(monkeypatch):
    repo = YFinanceSectorIndustryRepository()

    monkeypatch.setattr(
        "openmarkets.repositories.sector_industry.yf.Sector",
        lambda sector, session=None: SimpleNamespace(research_reports=[]),
    )

    assert repo.get_sector_research_reports("tech") == []

    # With reports
    monkeypatch.setattr(
        "openmarkets.repositories.sector_industry.yf.Sector",
        lambda sector, session=None: SimpleNamespace(
            research_reports=[{"id": "r1", "headHtml": "h", "provider": "p", "reportTitle": "t", "reportType": "t"}]
        ),
    )

    res = repo.get_sector_research_reports("tech")
    assert len(res) == 1


def test_get_industry_top_companies_and_variants(monkeypatch):
    repo = YFinanceSectorIndustryRepository()

    # None data returns empty
    monkeypatch.setattr(
        "openmarkets.repositories.sector_industry.yf.Industry",
        lambda industry, session=None: SimpleNamespace(
            top_companies=None, top_growth_companies=None, top_performing_companies=None
        ),
    )

    assert repo.get_industry_top_companies("x") == []
    assert repo.get_industry_top_growth_companies("x") == []
    assert repo.get_industry_top_performing_companies("x") == []

    # With data
    row = _RowLike(
        {
            "symbol": "A",
            "name": "Alpha",
            "market weight": 0.1,
            "ytd return": 1.2,
            "last price": 5.5,
            "target price": 6.7,
            "growth estimate": 0.3,
        }
    )
    df = _FakeDF([row])

    monkeypatch.setattr(
        "openmarkets.repositories.sector_industry.yf.Industry",
        lambda industry, session=None: SimpleNamespace(
            top_companies=df,
            top_growth_companies=df,
            top_performing_companies=df,
            overview={
                "companies_count": 1,
                "market_cap": 1,
                "message_board_id": "m",
                "description": "d",
                "industries_count": None,
                "market_weight": 0.1,
                "employee_count": 1,
            },
        ),
    )

    assert len(repo.get_industry_top_companies("x")) == 1
    assert len(repo.get_industry_top_growth_companies("x")) == 1
    assert len(repo.get_industry_top_performing_companies("x")) == 1
    assert repo.get_industry_overview("x").companies_count == 1
