from datetime import datetime

from openmarkets.schemas.holdings import (
    InsiderRosterHolder,
    StockInstitutionalHoldings,
    StockMutualFundHoldings,
)


def test_insider_roster_convert_dates_and_shares():
    # valid date string, None, invalid string
    r = InsiderRosterHolder(
        **{
            "Latest Transaction Date": "2020-02-01",
            "Position Direct Date": None,
            "Position Indirect Date": "not-a-date",
            "Shares Owned Directly": "100",
            "Shares Owned Indirectly": "NaN",
        }
    )

    assert isinstance(r.Latest_Transaction_Date, datetime)
    assert r.Latest_Transaction_Date.year == 2020
    assert r.Position_Direct_Date is None
    assert r.Position_Indirect_Date is None

    import math

    assert isinstance(r.Shares_Owned_Directly, float)
    assert r.Shares_Owned_Directly == 100.0
    val = r.Shares_Owned_Indirectly
    assert val is None or (isinstance(val, float) and math.isnan(val))


def test_insider_roster_shares_special_values_return_none():
    import math

    for val in ("nan", "NaN", "Inf", "-Inf"):
        r = InsiderRosterHolder(**{"Shares Owned Directly": val})
        v = r.Shares_Owned_Directly
        assert v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v)))


def test_institutional_and_mutual_convert_date():
    s = StockInstitutionalHoldings(**{"Date Report": "2021-03-04"})
    assert isinstance(s.Date_Report, datetime)
    assert s.Date_Report.year == 2021

    s2 = StockInstitutionalHoldings(**{"Date Report": "bad"})
    assert s2.Date_Report is None

    m = StockMutualFundHoldings(**{"Date Report": "2022-12-31"})
    assert isinstance(m.Date_Report, datetime)

    m2 = StockMutualFundHoldings(**{"Date Report": None})
    assert m2.Date_Report is None
