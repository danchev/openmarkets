from datetime import date, datetime

import pandas as pd
import pytest

from openmarkets.repositories.options import IOptionsRepository
from openmarkets.schemas.options import CallOption, OptionContractChain, OptionExpirationDate, PutOption
from openmarkets.services.options import OptionsService


def test_calloption_lasttradedate_accepts_pandas_timestamp():
    ts = pd.Timestamp("2025-12-18T00:00:00")
    call = CallOption(
        contractSymbol="AAPL231215C00100000",
        lastTradeDate=ts,
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


def test_putoption_lasttradedate_accepts_pandas_timestamp():
    ts = pd.Timestamp("2025-12-18T00:00:00")
    put = PutOption(
        contractSymbol="AAPL231215P00100000",
        lastTradeDate=ts,
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


class DummyOptionsRepository(IOptionsRepository):
    # Implement abstract methods to satisfy IOptionsRepository
    def get_option_expiration_dates(self, ticker):
        return self.fetch_option_expiration_dates(ticker)

    def get_option_chain(self, ticker, expiration=None):
        return self.fetch_option_chain(ticker, expiration)

    def get_call_options(self, ticker, expiration=None):
        return self.fetch_call_options(ticker, expiration)

    def get_put_options(self, ticker, expiration=None):
        return self.fetch_put_options(ticker, expiration)

    def get_options_volume_analysis(self, ticker, expiration_date=None):
        return self.fetch_options_volume_analysis(ticker, expiration_date)

    async def get_options_by_moneyness(self, ticker, expiration_date=None, moneyness_range=0.1):
        return await self.fetch_options_by_moneyness(ticker, expiration_date, moneyness_range)

    async def get_options_skew(self, ticker, expiration_date=None):
        return await self.fetch_options_skew(ticker, expiration_date)

    def fetch_option_expiration_dates(self, ticker):
        return [OptionExpirationDate(date=datetime(2025, 12, 19))]

    def fetch_option_chain(self, ticker, expiration):
        return OptionContractChain(calls=[], puts=[], underlying=None)

    def fetch_call_options(self, ticker, expiration):
        return [
            CallOption(
                contractSymbol="AAPL231215C00100000",
                lastTradeDate=datetime(2025, 12, 18),
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
        ]

    def fetch_put_options(self, ticker, expiration):
        return [
            PutOption(
                contractSymbol="AAPL231215P00100000",
                lastTradeDate=datetime(2025, 12, 18),
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
        ]

    def fetch_options_volume_analysis(self, ticker, expiration_date):
        return {"total_call_volume": 100, "total_put_volume": 50}

    async def fetch_options_by_moneyness(self, ticker, expiration_date, moneyness_range):
        return {"calls": [], "puts": []}

    async def fetch_options_skew(self, ticker, expiration_date):
        return {"call_skew": [], "put_skew": []}


@pytest.fixture
def service():
    return OptionsService(repository=DummyOptionsRepository())


def test_get_option_expiration_dates(service):
    result = service.get_option_expiration_dates("AAPL")
    assert isinstance(result, list)
    assert isinstance(result[0], OptionExpirationDate)


def test_get_option_chain(service):
    result = service.get_option_chain("AAPL", date(2025, 12, 19))
    assert hasattr(result, "calls")
    assert hasattr(result, "puts")


def test_get_call_options(service):
    result = service.get_call_options("AAPL", date(2025, 12, 19))
    assert isinstance(result, list)
    assert isinstance(result[0], CallOption)


def test_get_put_options(service):
    result = service.get_put_options("AAPL", date(2025, 12, 19))
    assert isinstance(result, list)
    assert isinstance(result[0], PutOption)


def test_get_options_volume_analysis(service):
    result = service.get_options_volume_analysis("AAPL", "2025-12-19")
    assert "total_call_volume" in result
    assert "total_put_volume" in result


@pytest.mark.asyncio
async def test_get_options_by_moneyness(service):
    result = await service.get_options_by_moneyness("AAPL", "2025-12-19", 0.1)
    assert "calls" in result
    assert "puts" in result


@pytest.mark.asyncio
async def test_get_options_skew(service):
    result = await service.get_options_skew("AAPL", "2025-12-19")
    assert "call_skew" in result
    assert "put_skew" in result
