from datetime import datetime

import pandas as pd

from openmarkets.schemas.options import CallOption, OptionExpirationDate, PutOption


def test_parse_last_trade_date_with_timestamp():
    ts = pd.Timestamp("2020-01-01T12:00:00Z")

    c = CallOption(
        contractSymbol="C1",
        lastTradeDate=ts,
        strike=1.0,
        lastPrice=1.0,
        bid=0.5,
        ask=0.6,
        change=0.1,
        percentChange=1.0,
        impliedVolatility=0.2,
        inTheMoney=False,
        contractSize="100",
        currency="USD",
    )

    assert isinstance(c.lastTradeDate, datetime)


def test_parse_last_trade_date_with_datetime_passes_through():
    dt = datetime.utcnow()

    p = PutOption(
        contractSymbol="P1",
        lastTradeDate=dt,
        strike=1.0,
        lastPrice=1.0,
        bid=0.5,
        ask=0.6,
        change=0.1,
        percentChange=1.0,
        impliedVolatility=0.2,
        inTheMoney=False,
        contractSize="100",
        currency="USD",
    )

    assert p.lastTradeDate is dt


def test_option_expiration_date_alias():
    o = OptionExpirationDate(date="2020-01-01T00:00:00Z")
    assert hasattr(o, "date_")
    assert isinstance(o.date_, datetime)
