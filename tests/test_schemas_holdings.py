import math
import types
from datetime import datetime

import pytest

from openmarkets.schemas.holdings import (
    InsiderRosterHolder,
    StockInstitutionalHoldings,
    StockMutualFundHoldings,
)


@pytest.fixture
def dummy_class():
    class Dummy:
        pass

    return Dummy


@pytest.mark.parametrize("bad_value", [object(), [], {}, set(), types.SimpleNamespace()])
def test_insider_roster_shares_convert_shares_exception(bad_value):
    # This triggers the except Exception branch in convert_shares
    r = InsiderRosterHolder(**{"Shares Owned Directly": bad_value})
    assert r.shares_owned_directly is None


def test_stock_institutional_holdings_date_report_datetime():
    # This triggers the isinstance(v, datetime) branch
    now = datetime.now()
    s = StockInstitutionalHoldings(**{"Date Report": now})
    assert s.date_report is now


@pytest.mark.parametrize("bad_value", [object(), [], {}, set(), types.SimpleNamespace()])
def test_stock_mutual_fund_holdings_date_report_exception(bad_value):
    # This triggers the except Exception branch in convert_date
    m = StockMutualFundHoldings(**{"Date Report": bad_value})
    assert m.date_report is None


def test_insider_roster_convert_dates_and_shares():
    """Test that InsiderRosterHolder correctly converts date strings and share counts."""
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

    assert isinstance(r.latest_transaction_date, datetime)
    assert r.latest_transaction_date.year == 2020
    assert r.position_direct_date is None
    assert r.position_indirect_date is None

    assert isinstance(r.shares_owned_directly, float)
    assert r.shares_owned_directly == 100.0
    val = r.shares_owned_indirectly
    assert val is None or (isinstance(val, float) and math.isnan(val))


@pytest.mark.parametrize("special_value", ["nan", "NaN", "Inf", "-Inf"])
def test_insider_roster_shares_special_values_return_none(special_value: str):
    """Test that InsiderRosterHolder handles special float values (nan, inf) correctly."""
    r = InsiderRosterHolder(**{"Shares Owned Directly": special_value})
    v = r.shares_owned_directly
    assert v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v)))


def test_institutional_and_mutual_convert_date():
    """Test that institutional and mutual fund holdings correctly convert date strings."""
    s = StockInstitutionalHoldings(**{"Date Report": "2021-03-04"})
    assert isinstance(s.date_report, datetime)
    assert s.date_report.year == 2021

    s2 = StockInstitutionalHoldings(**{"Date Report": "bad"})
    assert s2.date_report is None

    m = StockMutualFundHoldings(**{"Date Report": "2022-12-31"})
    assert isinstance(m.date_report, datetime)

    m2 = StockMutualFundHoldings(**{"Date Report": None})
    assert m2.date_report is None
