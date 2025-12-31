from datetime import date, datetime

import pandas as pd
import pytest

from openmarkets.repositories.options import IOptionsRepository
from openmarkets.schemas.options import CallOption, OptionContractChain, OptionExpirationDate, PutOption
from openmarkets.services.options import OptionsService


@pytest.fixture
def last_trade_timestamp() -> pd.Timestamp:
    return pd.Timestamp("2025-12-18T00:00:00")


@pytest.mark.parametrize(
    ("model", "contract_symbol", "in_the_money"),
    [
        (CallOption, "AAPL231215C00100000", True),
        (PutOption, "AAPL231215P00100000", False),
    ],
)
def test_option_last_trade_date_accepts_pandas_timestamp(model, contract_symbol, in_the_money, last_trade_timestamp):
    option = model(
        contractSymbol=contract_symbol,
        lastTradeDate=last_trade_timestamp,
        strike=100,
        lastPrice=5.0,
        bid=4.9,
        ask=5.1,
        change=0.1,
        percentChange=0.02,
        volume=10,
        openInterest=100,
        impliedVolatility=0.2,
        inTheMoney=in_the_money,
        contractSize="REGULAR",
        currency="USD",
    )

    assert isinstance(option.last_trade_date, datetime)
    assert option.last_trade_date == datetime(2025, 12, 18)


class OptionsRepositoryStub(IOptionsRepository):
    def get_option_expiration_dates(self, ticker, session=None):
        return [OptionExpirationDate(date=datetime(2025, 12, 19))]

    def get_option_chain(self, ticker, expiration, session=None):
        return OptionContractChain(calls=[], puts=[], underlying=None)

    def get_call_options(self, ticker, expiration, session=None):
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

    def get_put_options(self, ticker, expiration, session=None):
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

    def get_options_volume_analysis(self, ticker, expiration_date, session=None):
        return {"total_call_volume": 100, "total_put_volume": 50}

    def get_options_by_moneyness(self, ticker, expiration_date, moneyness_range, session=None):
        return {"calls": [], "puts": []}

    def get_options_skew(self, ticker, expiration_date, session=None):
        return {"call_skew": [], "put_skew": []}


@pytest.fixture
def options_service() -> OptionsService:
    return OptionsService(repository=OptionsRepositoryStub())


def test_get_option_expiration_dates(options_service):
    result = options_service.get_option_expiration_dates("AAPL")
    assert isinstance(result, list)
    assert isinstance(result[0], OptionExpirationDate)


def test_get_option_chain(options_service):
    result = options_service.get_option_chain("AAPL", date(2025, 12, 19))
    assert hasattr(result, "calls")
    assert hasattr(result, "puts")


def test_get_call_options(options_service):
    result = options_service.get_call_options("AAPL", date(2025, 12, 19))
    assert isinstance(result, list)
    assert isinstance(result[0], CallOption)


def test_get_put_options(options_service):
    result = options_service.get_put_options("AAPL", date(2025, 12, 19))
    assert isinstance(result, list)
    assert isinstance(result[0], PutOption)


def test_get_options_volume_analysis(options_service):
    result = options_service.get_options_volume_analysis("AAPL", "2025-12-19")
    assert "total_call_volume" in result
    assert "total_put_volume" in result


def test_get_options_by_moneyness(options_service):
    result = options_service.get_options_by_moneyness("AAPL", "2025-12-19", 0.1)
    assert "calls" in result
    assert "puts" in result


def test_get_options_skew(options_service):
    result = options_service.get_options_skew("AAPL", "2025-12-19")
    assert "call_skew" in result
    assert "put_skew" in result
