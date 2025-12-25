from datetime import datetime

from openmarkets.schemas.options import CallOption, PutOption


def test_calloption_lasttradedate_accepts_datetime():
    dt = datetime(2025, 12, 18)
    call = CallOption(
        contractSymbol="AAPL231215C00100000",
        lastTradeDate=dt,
        strike=100,
        lastPrice=5.0,
        bid=4.9,
        ask=5.1,
        change=0.1,
        percentChange=0.02,
        volume=10,
        openInterest=100,
        impliedVolatility=0.2,
        inTheMoney=True,
        contractSize="REGULAR",
        currency="USD",
    )
    assert call.lastTradeDate == dt


def test_calloption_lasttradedate_accepts_str():
    # Should parse ISO string to datetime
    s = "2025-12-18T00:00:00"
    call = CallOption(
        contractSymbol="AAPL231215C00100000",
        lastTradeDate=s,
        strike=100,
        lastPrice=5.0,
        bid=4.9,
        ask=5.1,
        change=0.1,
        percentChange=0.02,
        volume=10,
        openInterest=100,
        impliedVolatility=0.2,
        inTheMoney=True,
        contractSize="REGULAR",
        currency="USD",
    )
    assert isinstance(call.lastTradeDate, datetime)
    assert call.lastTradeDate == datetime(2025, 12, 18)


def test_putoption_lasttradedate_accepts_datetime():
    dt = datetime(2025, 12, 18)
    put = PutOption(
        contractSymbol="AAPL231215P00100000",
        lastTradeDate=dt,
        strike=100,
        lastPrice=5.0,
        bid=4.9,
        ask=5.1,
        change=0.1,
        percentChange=0.02,
        volume=10,
        openInterest=100,
        impliedVolatility=0.2,
        inTheMoney=False,
        contractSize="REGULAR",
        currency="USD",
    )
    assert put.lastTradeDate == dt


def test_putoption_lasttradedate_accepts_str():
    s = "2025-12-18T00:00:00"
    put = PutOption(
        contractSymbol="AAPL231215P00100000",
        lastTradeDate=s,
        strike=100,
        lastPrice=5.0,
        bid=4.9,
        ask=5.1,
        change=0.1,
        percentChange=0.02,
        volume=10,
        openInterest=100,
        impliedVolatility=0.2,
        inTheMoney=False,
        contractSize="REGULAR",
        currency="USD",
    )
    assert isinstance(put.lastTradeDate, datetime)
    assert put.lastTradeDate == datetime(2025, 12, 18)
