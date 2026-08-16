"""Unit tests for YFinanceOptionsRepository."""

import pandas as pd
import pytest

from openmarkets.core.exceptions import APIError, DataUnavailableError, ProviderContractError
from openmarkets.repositories.options import YFinanceOptionsRepository
from openmarkets.schemas.options import OptionExpirationDate


@pytest.fixture
def options_repository() -> YFinanceOptionsRepository:
    """Fixture for YFinanceOptionsRepository instance."""
    return YFinanceOptionsRepository()


@pytest.fixture
def sample_call_option_data() -> dict:
    """Sample call option data for testing."""
    return {
        "contractSymbol": "C1",
        "lastTradeDate": pd.Timestamp("2023-01-01"),
        "strike": 100,
        "lastPrice": 1.0,
        "bid": 0.9,
        "ask": 1.1,
        "change": 0.1,
        "percentChange": 10.0,
        "volume": 10,
        "openInterest": 5,
        "impliedVolatility": 0.5,
        "inTheMoney": True,
        "contractSize": "100",
        "currency": "USD",
    }


@pytest.fixture
def sample_put_option_data() -> dict:
    """Sample put option data for testing."""
    return {
        "contractSymbol": "P1",
        "lastTradeDate": pd.Timestamp("2023-01-01"),
        "strike": 90,
        "lastPrice": 1.5,
        "bid": 1.4,
        "ask": 1.6,
        "change": -0.1,
        "percentChange": -5.0,
        "volume": 20,
        "openInterest": 10,
        "impliedVolatility": 0.6,
        "inTheMoney": False,
        "contractSize": "100",
        "currency": "USD",
    }


def test_get_option_expiration_dates(options_repository, monkeypatch, dummy_ticker):
    """Test retrieving option expiration dates."""
    monkeypatch.setattr(
        "openmarkets.repositories.options.yf",
        type("Y", (), {"Ticker": lambda t, session=None: dummy_ticker(options=["2023-01-01", "2023-02-01"])}),
    )
    res = options_repository.get_option_expiration_dates("AAPL")
    assert isinstance(res, list)
    assert all(isinstance(x, OptionExpirationDate) for x in res)


def test_get_call_put_options_empty(options_repository, monkeypatch, dummy_ticker, dummy_option_chain, fake_dataframe):
    """Test getting call/put options when data is empty."""
    chain = dummy_option_chain(calls=fake_dataframe(), puts=fake_dataframe())
    monkeypatch.setattr(
        "openmarkets.repositories.options.yf",
        type("Y", (), {"Ticker": lambda t, session=None: dummy_ticker(option_chain=chain)}),
    )
    assert options_repository.get_call_options("AAPL") is None
    assert options_repository.get_put_options("AAPL") is None


def test_get_call_put_options_nonempty(
    options_repository,
    monkeypatch,
    dummy_ticker,
    dummy_option_chain,
    fake_dataframe,
    sample_call_option_data,
    sample_put_option_data,
):
    """Test getting call/put options with valid data."""
    calls = fake_dataframe([sample_call_option_data])
    puts = fake_dataframe([sample_put_option_data])
    chain = dummy_option_chain(calls=calls, puts=puts, underlying={"symbol": "AAPL"})
    monkeypatch.setattr(
        "openmarkets.repositories.options.yf",
        type("Y", (), {"Ticker": lambda t, session=None: dummy_ticker(option_chain=chain)}),
    )
    calls_res = options_repository.get_call_options("AAPL")
    puts_res = options_repository.get_put_options("AAPL")
    assert isinstance(calls_res, list) and calls_res[0].strike == 100
    assert isinstance(puts_res, list) and puts_res[0].strike == 90


def test_get_options_volume_analysis_no_expirations(options_repository, monkeypatch, dummy_ticker):
    """Test volume analysis when no expirations available."""
    monkeypatch.setattr(
        "openmarkets.repositories.options.yf",
        type("Y", (), {"Ticker": lambda t, session=None: dummy_ticker(options=[])}),
    )
    with pytest.raises(DataUnavailableError):
        options_repository.get_options_volume_analysis("AAPL")


def test_get_options_volume_analysis_with_data(
    options_repository, monkeypatch, dummy_ticker, dummy_option_chain, fake_dataframe
):
    """Test volume analysis with valid data."""
    calls = fake_dataframe([{"volume": 10, "openInterest": 5}])
    puts = fake_dataframe([{"volume": 20, "openInterest": 10}])
    chain = dummy_option_chain(calls=calls, puts=puts)

    def maker(t, session=None):
        return dummy_ticker(options=["2023-01-01"], option_chain=chain)

    monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": maker}))
    out = options_repository.get_options_volume_analysis("AAPL")
    assert out.total_call_volume == 10
    assert out.total_put_volume == 20
    assert out.put_call_ratio_volume == pytest.approx(20 / 10)


def test_get_options_by_moneyness_errors(options_repository, monkeypatch, dummy_ticker):
    """Test options by moneyness when current price unavailable."""
    monkeypatch.setattr(
        "openmarkets.repositories.options.yf",
        type("Y", (), {"Ticker": lambda t, session=None: dummy_ticker(info={})}),
    )
    with pytest.raises(DataUnavailableError):
        options_repository.get_options_by_moneyness("AAPL")


def test_get_options_by_moneyness_success(options_repository, monkeypatch, dummy_ticker, dummy_option_chain):
    """Test successful options by moneyness calculation."""
    calls = pd.DataFrame([{"strike": 100, "impliedVolatility": 0.2}])
    puts = pd.DataFrame([{"strike": 100, "impliedVolatility": 0.1}])
    chain = dummy_option_chain(calls=calls, puts=puts)

    class Maker:
        def __init__(self, t, session=None):
            self.info = {"currentPrice": 100}
            self.options = ["2023-01-01"]
            self._option_chain = chain

        def option_chain(self, date=None):
            return self._option_chain

    monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": Maker}))
    res = options_repository.get_options_by_moneyness("AAPL")
    assert res.current_price == 100
    assert res.calls and res.puts


def test_get_options_skew_no_expirations(options_repository, monkeypatch, dummy_ticker):
    """Test options skew when no expirations available."""

    class T1:
        def __init__(self, t, session=None):
            self.options = []

    monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": T1}))
    with pytest.raises(DataUnavailableError):
        options_repository.get_options_skew("AAPL")


def test_get_options_skew_empty_chain(options_repository, monkeypatch, dummy_ticker, dummy_option_chain):
    """Test options skew when option chain is empty."""

    class T2:
        def __init__(self, t, session=None):
            self.options = ["2023-01-01"]

        def option_chain(self, date=None):
            return dummy_option_chain()

    monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": T2}))
    with pytest.raises(DataUnavailableError):
        options_repository.get_options_skew("AAPL")


def test_get_options_skew_missing_columns(options_repository, monkeypatch, dummy_ticker, dummy_option_chain):
    """Test options skew when required columns are missing."""
    calls = pd.DataFrame([{"wrong": 1}])
    puts = pd.DataFrame([{"wrong": 2}])
    chain = dummy_option_chain(calls=calls, puts=puts)

    class T3:
        def __init__(self, t, session=None):
            self.options = ["2023-01-01"]
            self._option_chain = chain

        def option_chain(self, date=None):
            return self._option_chain

    monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": T3}))
    with pytest.raises(DataUnavailableError):
        options_repository.get_options_skew("AAPL")


def test_get_options_skew_keeps_usable_side(options_repository, monkeypatch, dummy_option_chain):
    """A malformed side must not discard the side that is usable.

    Previously the error dict from one side replaced the whole response, so
    valid call skew data was silently thrown away when puts were malformed.
    """
    calls = pd.DataFrame([{"strike": 100, "impliedVolatility": 0.5}])
    puts = pd.DataFrame([{"strike": 100}])  # missing impliedVolatility
    chain = dummy_option_chain(calls=calls, puts=puts)

    class T:
        def __init__(self, t, session=None):
            self.options = ["2023-01-01"]
            self._option_chain = chain

        def option_chain(self, date=None):
            return self._option_chain

    monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": T}))
    out = options_repository.get_options_skew("AAPL")

    assert [(p.strike, p.implied_volatility) for p in out.call_skew] == [(100, 0.5)]
    assert out.put_skew == []
    assert out.warning is not None and "puts" in out.warning


def test_get_options_skew_success(options_repository, monkeypatch, dummy_ticker, dummy_option_chain):
    """Test successful options skew calculation."""
    calls = pd.DataFrame([{"strike": 100, "impliedVolatility": 0.5}])
    puts = pd.DataFrame([{"strike": 100, "impliedVolatility": 0.4}])
    chain = dummy_option_chain(calls=calls, puts=puts)

    class T4:
        def __init__(self, t, session=None):
            self.options = ["2023-01-01"]
            self._option_chain = chain

        def option_chain(self, date=None):
            return self._option_chain

    monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": T4}))
    out = options_repository.get_options_skew("AAPL")
    assert out.call_skew and out.put_skew


def test_get_option_chain_with_data(
    options_repository,
    monkeypatch,
    dummy_ticker,
    dummy_option_chain,
    fake_dataframe,
    sample_call_option_data,
    sample_put_option_data,
):
    """Test get_option_chain with both calls and puts."""
    calls = fake_dataframe([sample_call_option_data])
    puts = fake_dataframe([sample_put_option_data])
    chain = dummy_option_chain(calls=calls, puts=puts, underlying={"symbol": "AAPL"})
    monkeypatch.setattr(
        "openmarkets.repositories.options.yf",
        type("Y", (), {"Ticker": lambda t, session=None: dummy_ticker(option_chain=chain)}),
    )
    result = options_repository.get_option_chain("AAPL")
    assert result.calls is not None
    assert result.puts is not None
    assert len(result.calls) == 1
    assert len(result.puts) == 1


def test_get_options_by_moneyness_no_chain(options_repository, monkeypatch, dummy_ticker):
    """Test get_options_by_moneyness when chain is not available."""

    class Maker:
        def __init__(self, t, session=None):
            self.info = {"currentPrice": 100}
            self.options = []

        def option_chain(self, date=None):
            return None

    monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": Maker}))
    with pytest.raises(DataUnavailableError):
        options_repository.get_options_by_moneyness("AAPL")


def test_safe_ratio_zero_denominator(options_repository):
    """Test _safe_ratio with zero denominator."""
    assert options_repository._safe_ratio(10.0, 0.0) is None
    assert options_repository._safe_ratio(10.0, 5.0) == 2.0


def test_get_column_sum_missing_column(options_repository, fake_dataframe):
    """Test _get_column_sum with missing column."""
    df = fake_dataframe([{"volume": 10}])
    assert options_repository._get_column_sum(df, "volume") == 10
    with pytest.raises(ProviderContractError, match="missing_col"):
        options_repository._get_column_sum(df, "missing_col")


def test_option_chain_exception_handling(options_repository, monkeypatch):
    """Test exception handling in _get_option_chain_for_expiration."""

    class FailingTicker:
        def __init__(self, t, session=None):
            self.options = ["2023-01-01"]

        def option_chain(self, date=None):
            raise Exception("Simulated failure")

    monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": FailingTicker}))
    with pytest.raises(APIError, match="Simulated failure"):
        options_repository.get_options_volume_analysis("AAPL")


@pytest.mark.parametrize("invalid_range", [-0.1, 1.1, float("nan"), float("inf")])
def test_moneyness_range_must_be_finite_and_bounded(options_repository, invalid_range):
    with pytest.raises(ValueError, match="moneyness_range"):
        options_repository.get_options_by_moneyness("AAPL", moneyness_range=invalid_range)


def test_nan_current_price_is_unavailable(options_repository, monkeypatch):
    monkeypatch.setattr(
        "openmarkets.repositories.options.yf.Ticker",
        lambda ticker, session=None: type("Ticker", (), {"info": {"currentPrice": float("nan")}})(),
    )
    with pytest.raises(DataUnavailableError, match="current stock price"):
        options_repository.get_options_by_moneyness("AAPL")
