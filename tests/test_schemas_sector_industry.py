from openmarkets.schemas.sector_industry import IndustryResearchReportEntry


def test_validate_target_price_with_none():
    data = {
        "id": "r1",
        "headHtml": "head",
        "provider": "p",
        "reportTitle": "t",
        "reportType": "type",
        "targetPrice": None,
    }

    r = IndustryResearchReportEntry(**data)
    assert r.target_price is None


def test_validate_target_price_with_float_string():
    data = {
        "id": "r2",
        "headHtml": "head",
        "provider": "p",
        "reportTitle": "t",
        "reportType": "type",
        "targetPrice": "12.34",
    }

    r = IndustryResearchReportEntry(**data)
    assert isinstance(r.target_price, float)
    assert r.target_price == 12.34


def test_validate_target_price_with_non_numeric_returns_none():
    data = {
        "id": "r3",
        "headHtml": "head",
        "provider": "p",
        "reportTitle": "t",
        "reportType": "type",
        "targetPrice": "N/A",
    }

    r = IndustryResearchReportEntry(**data)
    assert r.target_price is None


def test_validate_target_price_with_float_value():
    data = {
        "id": "r4",
        "headHtml": "head",
        "provider": "p",
        "reportTitle": "t",
        "reportType": "type",
        "targetPrice": 7,
    }

    r = IndustryResearchReportEntry(**data)
    assert isinstance(r.target_price, float)
    assert r.target_price == 7.0


def test_sector_top_companies_entry_tolerates_nan_rating_and_name():
    """Reproduces a real Yahoo Finance response found via tests/live: some
    companies have no rating and/or no name, and yfinance represents that
    with a pandas float NaN rather than None. Constructing directly with
    NaN (not the string "nan") previously raised a ValidationError."""
    from openmarkets.schemas.sector_industry import SectorTopCompaniesEntry

    entry = SectorTopCompaniesEntry(
        symbol="AMBQ",
        name=float("nan"),
        rating=float("nan"),
        **{"market weight": 0.0001},
    )

    assert entry.name is None
    assert entry.rating is None


def test_sector_top_mutual_funds_entry_tolerates_none_name():
    """Reproduces a real Yahoo Finance response: some mutual fund tickers
    resolve to a None name rather than a string."""
    from openmarkets.schemas.sector_industry import SectorTopMutualFundsEntry

    entry = SectorTopMutualFundsEntry(symbol="FFOQX", name=None)

    assert entry.name is None


def test_sector_top_mutual_funds_entry_tolerates_nan_name():
    """A pandas NaN name must be accepted, not just an explicit None.

    The original version of this test only passed name=None, which the
    widened `str | None` annotation accepts on its own - so it passed while
    the NaN case, the one that actually occurs in real data, still raised
    ValidationError because the validator had not been wired up here.
    """
    from openmarkets.schemas.sector_industry import SectorTopMutualFundsEntry

    entry = SectorTopMutualFundsEntry(symbol="FFOQX", name=float("nan"))

    assert entry.name is None


def test_sector_top_etfs_entry_tolerates_nan_name():
    """SectorTopETFsEntry is populated by the same data.items() pattern from
    the same upstream source as the mutual-funds model, so it carries the
    same exposure even though no NaN name is present in today's data."""
    from openmarkets.schemas.sector_industry import SectorTopETFsEntry

    entry = SectorTopETFsEntry(symbol="XLK", name=float("nan"))

    assert entry.name is None


def test_industry_top_companies_entry_tolerates_nan_rating_and_name():
    """Mirrors test_sector_top_companies_entry_tolerates_nan_rating_and_name
    for the industry-scoped equivalent."""
    from openmarkets.schemas.sector_industry import IndustryTopCompaniesEntry

    entry = IndustryTopCompaniesEntry(
        symbol="AMBQ",
        name=float("nan"),
        rating=float("nan"),
        **{"market weight": 0.0001},
    )

    assert entry.name is None
    assert entry.rating is None
