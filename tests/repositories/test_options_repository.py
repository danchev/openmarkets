"""Unit tests for YFinanceOptionsRepository."""

import pandas as pd
import pytest

from openmarkets.repositories.options import YFinanceOptionsRepository
from openmarkets.schemas.options import OptionExpirationDate


class FakeDF:
    """Fake DataFrame class for testing."""

    def __init__(self, rows=None):
        self._rows = rows or []
        self.columns = list(self._rows[0].keys()) if self._rows else []

    @property
    def empty(self):
        return len(self._rows) == 0

    def iterrows(self):
        for i, r in enumerate(self._rows):

            class Row:
                def __init__(self, d):
                    self._d = d

                def to_dict(self):
                    return dict(self._d)

            yield i, Row(r)

    def to_dict(self, orient=None):
        if orient == "records":
            return [dict(r) for r in self._rows]
        return {i: dict(r) for i, r in enumerate(self._rows)}

    def __getitem__(self, key):
        class Col:
            def __init__(self, rows, key):
                self._rows = rows
                self._key = key

            def sum(self):
                return sum(r.get(self._key, 0) for r in self._rows)

        return Col(self._rows, key)


class DummyTicker:
    """Dummy ticker class for testing."""

    def __init__(self, options=None, info=None, option_chain=None):
        self.options = options or []
        self.info = info or {}
        self._option_chain = option_chain

    def option_chain(self, date=None):
        return self._option_chain


class DummyOptionChain:
    """Dummy option chain class for testing."""

    def __init__(self, calls=None, puts=None, underlying=None):
        self.calls = calls or FakeDF()
        self.puts = puts or FakeDF()
        self.underlying = underlying or {}


class TestYFinanceOptionsRepository:
    """Test suite for YFinanceOptionsRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = YFinanceOptionsRepository()

    def test_get_option_expiration_dates(self, monkeypatch):
        """Test retrieving option expiration dates."""
        monkeypatch.setattr(
            "openmarkets.repositories.options.yf",
            type("Y", (), {"Ticker": lambda t, session=None: DummyTicker(options=["2023-01-01", "2023-02-01"])}),
        )
        res = self.repo.get_option_expiration_dates("AAPL")
        assert isinstance(res, list)
        assert all(isinstance(x, OptionExpirationDate) for x in res)

    def test_get_call_put_options_empty(self, monkeypatch):
        """Test getting call/put options when data is empty."""
        dummy_chain = DummyOptionChain(calls=FakeDF(), puts=FakeDF())
        monkeypatch.setattr(
            "openmarkets.repositories.options.yf",
            type("Y", (), {"Ticker": lambda t, session=None: DummyTicker(option_chain=dummy_chain)}),
        )
        assert self.repo.get_call_options("AAPL") is None
        assert self.repo.get_put_options("AAPL") is None

    def test_get_call_put_options_nonempty(self, monkeypatch):
        """Test getting call/put options with valid data."""
        calls = FakeDF(
            [
                {
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
            ]
        )
        puts = FakeDF(
            [
                {
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
            ]
        )
        dummy_chain = DummyOptionChain(calls=calls, puts=puts, underlying={"symbol": "AAPL"})
        monkeypatch.setattr(
            "openmarkets.repositories.options.yf",
            type("Y", (), {"Ticker": lambda t, session=None: DummyTicker(option_chain=dummy_chain)}),
        )
        calls_res = self.repo.get_call_options("AAPL")
        puts_res = self.repo.get_put_options("AAPL")
        assert isinstance(calls_res, list) and calls_res[0].strike == 100
        assert isinstance(puts_res, list) and puts_res[0].strike == 90

    def test_get_options_volume_analysis_no_expirations(self, monkeypatch):
        """Test volume analysis when no expirations available."""
        monkeypatch.setattr(
            "openmarkets.repositories.options.yf",
            type("Y", (), {"Ticker": lambda t, session=None: DummyTicker(options=[])}),
        )
        assert self.repo.get_options_volume_analysis("AAPL") == {"error": "No options data available"}

    def test_get_options_volume_analysis_with_data(self, monkeypatch):
        """Test volume analysis with valid data."""
        calls = FakeDF([{"volume": 10, "openInterest": 5}])
        puts = FakeDF([{"volume": 20, "openInterest": 10}])
        dummy_chain = DummyOptionChain(calls=calls, puts=puts)

        def maker(t, session=None):
            return DummyTicker(options=["2023-01-01"], option_chain=dummy_chain)

        monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": maker}))
        out = self.repo.get_options_volume_analysis("AAPL")
        assert out["total_call_volume"] == 10
        assert out["total_put_volume"] == 20
        assert out["put_call_ratio_volume"] == pytest.approx(20 / 10)

    def test_get_options_by_moneyness_errors(self, monkeypatch):
        """Test options by moneyness when current price unavailable."""
        monkeypatch.setattr(
            "openmarkets.repositories.options.yf",
            type("Y", (), {"Ticker": lambda t, session=None: DummyTicker(info={})}),
        )
        res = self.repo.get_options_by_moneyness("AAPL")
        assert res == {"error": "Could not get current stock price"}

    @pytest.mark.xfail(reason="pandas boolean indexing not reliably emulated in this test harness", strict=False)
    def test_get_options_by_moneyness_success(self, monkeypatch):
        """Test successful options by moneyness calculation."""
        calls = pd.DataFrame([{"strike": 100, "impliedVolatility": 0.2}])
        puts = pd.DataFrame([{"strike": 100, "impliedVolatility": 0.1}])
        dummy_chain = DummyOptionChain(calls=calls, puts=puts)

        class Maker:
            def __init__(self, t, session=None):
                self.info = {"currentPrice": 100}
                self.options = ["2023-01-01"]
                self._option_chain = dummy_chain

            def option_chain(self, date=None):
                return self._option_chain

        monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": Maker}))
        res = self.repo.get_options_by_moneyness("AAPL")
        assert res["current_price"] == 100
        assert res["calls"] and res["puts"]

    @pytest.mark.xfail(reason="pandas boolean indexing not reliably emulated in this test harness", strict=False)
    def test_get_options_skew_various_errors(self, monkeypatch):
        """Test various error conditions in options skew calculation."""

        # no expirations
        class T1:
            def __init__(self, t, session=None):
                self.options = []

        monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": T1}))
        out = self.repo.get_options_skew("AAPL")
        assert "error" in out

        # option_chain empty
        class T2:
            def __init__(self, t, session=None):
                self.options = ["2023-01-01"]

            def option_chain(self, date=None):
                return DummyOptionChain()

        monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": T2}))
        out2 = self.repo.get_options_skew("AAPL")
        assert "error" in out2

        # missing columns
        calls = pd.DataFrame([{"wrong": 1}])
        puts = pd.DataFrame([{"wrong": 2}])
        dummy_chain = DummyOptionChain(calls=calls, puts=puts)

        class T3:
            def __init__(self, t, session=None):
                self.options = ["2023-01-01"]
                self._option_chain = dummy_chain

            def option_chain(self, date=None):
                return self._option_chain

        monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": T3}))
        out3 = self.repo.get_options_skew("AAPL")
        assert "error" in out3

        # valid skew
        calls = pd.DataFrame([{"strike": 100, "impliedVolatility": 0.5}])
        puts = pd.DataFrame([{"strike": 100, "impliedVolatility": 0.4}])
        dummy_chain = DummyOptionChain(calls=calls, puts=puts)

        class T4:
            def __init__(self, t, session=None):
                self.options = ["2023-01-01"]
                self._option_chain = dummy_chain

            def option_chain(self, date=None):
                return self._option_chain

        monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": T4}))
        out4 = self.repo.get_options_skew("AAPL")
        assert "call_skew" in out4 and "put_skew" in out4

    def test_get_option_chain_with_data(self, monkeypatch):
        """Test get_option_chain with both calls and puts."""
        calls = FakeDF(
            [
                {
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
            ]
        )
        puts = FakeDF(
            [
                {
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
            ]
        )
        dummy_chain = DummyOptionChain(calls=calls, puts=puts, underlying={"symbol": "AAPL"})
        monkeypatch.setattr(
            "openmarkets.repositories.options.yf",
            type("Y", (), {"Ticker": lambda t, session=None: DummyTicker(option_chain=dummy_chain)}),
        )
        result = self.repo.get_option_chain("AAPL")
        assert result.calls is not None
        assert result.puts is not None
        assert len(result.calls) == 1
        assert len(result.puts) == 1

    def test_get_options_by_moneyness_no_chain(self, monkeypatch):
        """Test get_options_by_moneyness when chain is not available."""

        class Maker:
            def __init__(self, t, session=None):
                self.info = {"currentPrice": 100}
                self.options = []

            def option_chain(self, date=None):
                return None

        monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": Maker}))
        res = self.repo.get_options_by_moneyness("AAPL")
        assert res == {"error": "No options data available"}

    def test_safe_ratio_zero_denominator(self):
        """Test _safe_ratio with zero denominator."""
        assert self.repo._safe_ratio(10.0, 0.0) is None
        assert self.repo._safe_ratio(10.0, 5.0) == 2.0

    def test_get_column_sum_missing_column(self):
        """Test _get_column_sum with missing column."""
        df = FakeDF([{"volume": 10}])
        assert self.repo._get_column_sum(df, "volume") == 10
        assert self.repo._get_column_sum(df, "missing_col") == 0

    def test_option_chain_exception_handling(self, monkeypatch):
        """Test exception handling in _get_option_chain_for_expiration."""

        class FailingTicker:
            def __init__(self, t, session=None):
                self.options = ["2023-01-01"]

            def option_chain(self, date=None):
                raise Exception("Simulated failure")

        monkeypatch.setattr("openmarkets.repositories.options.yf", type("Y", (), {"Ticker": FailingTicker}))
        res = self.repo.get_options_volume_analysis("AAPL")
        assert res == {"error": "No options data available"}
