from datetime import datetime, timezone

import pandas as pd

from openmarkets.schemas.stock import StockDividends, StockInfo, StockInfo_v2


def test_stockinfo_timestamp_conversion():
    s = StockInfo(exDividendDate="1609459200")  # 2021-01-01T00:00:00Z
    assert isinstance(s.ex_dividend_date, datetime)

    s2 = StockInfo(exDividendDate=None)
    assert s2.ex_dividend_date is None

    dt = datetime.now(timezone.utc)
    s3 = StockInfo(exDividendDate=dt)
    assert s3.ex_dividend_date is dt

    s4 = StockInfo(exDividendDate="not-a-number")
    assert s4.ex_dividend_date is None


def test_stockdividends_parse_date_with_timestamp():
    ts = pd.Timestamp("2020-01-01T00:00:00Z")
    d = StockDividends(Date=ts, Dividends=0.5)
    assert isinstance(d.date_, datetime)


def test_stockinfo_v2_ex_dividend_conversion():
    s = StockInfo_v2(exDividendDate="1609459200")
    assert isinstance(s.ex_dividend_date, datetime)

    s2 = StockInfo_v2(exDividendDate=None)
    assert s2.ex_dividend_date is None

    s3 = StockInfo_v2(exDividendDate="bad")
    assert s3.ex_dividend_date is None
