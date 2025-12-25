from types import SimpleNamespace

import pandas as pd
import pytest

from openmarkets.repositories.options import YFinanceOptionsRepository
from openmarkets.schemas.options import OptionExpirationDate


def test_get_option_expiration_dates(monkeypatch):
    repo = YFinanceOptionsRepository()

    monkeypatch.setattr(
        "openmarkets.repositories.options.yf.Ticker",
        lambda t, session=None: SimpleNamespace(options=["2020-01-01", "2020-02-01"]),
    )

    out = repo.get_option_expiration_dates("A")
    assert isinstance(out, list)
    assert isinstance(out[0], OptionExpirationDate)


def _make_option_df(rows):
    return pd.DataFrame(rows)


def test_get_option_chain_and_call_put_options(monkeypatch):
    repo = YFinanceOptionsRepository()

    calls = _make_option_df(
        [
            {
                "contractSymbol": "C1",
                "lastTradeDate": pd.Timestamp("2020-01-01T12:00:00Z"),
                "strike": 100.0,
                "lastPrice": 1.0,
                "bid": 0.5,
                "ask": 0.6,
                "change": 0.1,
                "percentChange": 1.0,
                "volume": 10,
                "openInterest": 100,
                "impliedVolatility": 0.2,
                "inTheMoney": False,
                "contractSize": "100",
                "currency": "USD",
            }
        ]
    )

    puts = _make_option_df([])

    class FakeOptionChain:
        def __init__(self, calls, puts):
            self.calls = calls
            self.puts = puts
            self.underlying = {"symbol": "A"}

    monkeypatch.setattr(
        "openmarkets.repositories.options.yf.Ticker",
        lambda t, session=None: SimpleNamespace(option_chain=lambda date=None: FakeOptionChain(calls, puts)),
    )

    oc = repo.get_option_chain("A")
    assert oc.calls is not None
    assert len(oc.calls) == 1

    calls_list = repo.get_call_options("A")
    assert isinstance(calls_list, list)

    puts_list = repo.get_put_options("A")
    assert puts_list is None


def test_get_options_volume_analysis_and_helpers(monkeypatch):
    repo = YFinanceOptionsRepository()

    calls = pd.DataFrame(
        [
            {"volume": 10, "openInterest": 100},
            {"volume": 5, "openInterest": 50},
        ]
    )
    puts = pd.DataFrame(
        [
            {"volume": 3, "openInterest": 30},
        ]
    )

    class FakeOptionChain:
        def __init__(self):
            self.calls = calls
            self.puts = puts

    class FakeStock:
        def __init__(self):
            self.options = ["2020-01-01"]

        def option_chain(self, exp):
            return FakeOptionChain()

    monkeypatch.setattr("openmarkets.repositories.options.yf.Ticker", lambda t, session=None: FakeStock())

    analysis = repo.get_options_volume_analysis("A")
    assert analysis["total_call_volume"] == 15
    assert analysis["total_put_volume"] == 3
    assert analysis["put_call_ratio_volume"] == pytest.approx(3 / 15)

    # _safe_ratio denominator 0
    assert repo._safe_ratio(1, 0) is None
    assert repo._get_column_sum(calls, "missing") == 0
    assert repo._get_column_sum(calls, "volume") == 15


def test_get_options_by_moneyness_errors_and_success(monkeypatch):
    repo = YFinanceOptionsRepository()

    # missing price
    monkeypatch.setattr("openmarkets.repositories.options.yf.Ticker", lambda t, session=None: SimpleNamespace(info={}))
    assert repo.get_options_by_moneyness("A")["error"]

    # with price and chain
    class FakeStock:
        def __init__(self):
            self.info = {"currentPrice": 100}
            self.options = ["2020-01-01"]

        def option_chain(self, exp):
            calls = pd.DataFrame([{"strike": 95, "impliedVolatility": 0.1}])
            puts = pd.DataFrame([{"strike": 105, "impliedVolatility": 0.2}])
            return SimpleNamespace(calls=calls, puts=puts)

    monkeypatch.setattr("openmarkets.repositories.options.yf.Ticker", lambda t, session=None: FakeStock())

    res = repo.get_options_by_moneyness("A", moneyness_range=0.1)
    assert "calls" in res and "puts" in res


def test_get_options_skew_various_cases(monkeypatch):
    repo = YFinanceOptionsRepository()

    # chain None
    monkeypatch.setattr("openmarkets.repositories.options.yf.Ticker", lambda t, session=None: SimpleNamespace())
    out = repo.get_options_skew("A", "2020-01-01")
    assert "error" in out

    # both empty
    class FakeStockEmpty:
        def __init__(self):
            self.options = ["d"]

        def option_chain(self, exp):
            return SimpleNamespace(calls=pd.DataFrame(), puts=pd.DataFrame())

    monkeypatch.setattr("openmarkets.repositories.options.yf.Ticker", lambda t, session=None: FakeStockEmpty())
    out = repo.get_options_skew("A")
    assert "error" in out

    # missing columns
    calls = pd.DataFrame([{"volume": 1}])
    monkeypatch.setattr(
        "openmarkets.repositories.options.yf.Ticker",
        lambda t, session=None: SimpleNamespace(
            option_chain=lambda exp: SimpleNamespace(calls=calls, puts=pd.DataFrame())
        ),
    )
    res = repo.get_options_skew("A")
    assert "error" in res or isinstance(res.get("call_skew"), list)

    # valid skew
    calls = pd.DataFrame([{"strike": 10, "impliedVolatility": 0.1}])
    puts = pd.DataFrame([{"strike": 9, "impliedVolatility": 0.2}])
    monkeypatch.setattr(
        "openmarkets.repositories.options.yf.Ticker",
        lambda t, session=None: SimpleNamespace(
            options=["d"], option_chain=lambda exp: SimpleNamespace(calls=calls, puts=puts)
        ),
    )
    res = repo.get_options_skew("A")
    assert "call_skew" in res and "put_skew" in res
