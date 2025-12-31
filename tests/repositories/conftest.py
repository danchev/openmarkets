from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd
import pytest

from openmarkets.repositories.analysis import YFinanceAnalysisRepository
from openmarkets.repositories.crypto import YFinanceCryptoRepository
from openmarkets.repositories.financials import YFinanceFinancialsRepository
from openmarkets.repositories.funds import YFinanceFundsRepository
from openmarkets.repositories.holdings import YFinanceHoldingsRepository
from openmarkets.repositories.markets import YFinanceMarketsRepository
from openmarkets.repositories.options import YFinanceOptionsRepository
from openmarkets.repositories.sector_industry import YFinanceSectorIndustryRepository
from openmarkets.repositories.stock import YFinanceStockRepository
from openmarkets.repositories.technical_analysis import YFinanceTechnicalAnalysisRepository


@pytest.fixture
def stock_ticker() -> str:
    return "AAPL"


@pytest.fixture
def patch_yf(monkeypatch):
    """Helper to monkeypatch yfinance in a given module."""

    def _patch(module_path: str, mock_yf: Any) -> None:
        monkeypatch.setattr(module_path + ".yf", mock_yf)

    return _patch


@pytest.fixture
def ohlcv_history_factory() -> Callable[[list[dict[str, Any]]], pd.DataFrame]:
    """Factory for building OHLCV history DataFrames from dict records."""

    def _make(records: list[dict[str, Any]]) -> pd.DataFrame:
        return pd.DataFrame(records)

    return _make


@pytest.fixture
def stock_repository() -> YFinanceStockRepository:
    return YFinanceStockRepository()


class FakeDataFrame:
    """Fake DataFrame for options testing."""

    def __init__(self, rows: list[dict[str, Any]] | None = None):
        self._rows = rows or []
        self.columns = list(self._rows[0].keys()) if self._rows else []

    @property
    def empty(self) -> bool:
        return len(self._rows) == 0

    def iterrows(self):
        for i, r in enumerate(self._rows):

            class Row:
                def __init__(self, d: dict[str, Any]):
                    self._d = d

                def to_dict(self) -> dict[str, Any]:
                    return dict(self._d)

            yield i, Row(r)

    def to_dict(self, orient: str | None = None) -> dict[int, dict[str, Any]] | list[dict[str, Any]]:
        if orient == "records":
            return [dict(r) for r in self._rows]
        return {i: dict(r) for i, r in enumerate(self._rows)}

    def __getitem__(self, key: str):
        class Col:
            def __init__(self, rows: list[dict[str, Any]], key: str):
                self._rows = rows
                self._key = key

            def sum(self) -> float:
                return sum(r.get(self._key, 0) for r in self._rows)

        return Col(self._rows, key)


@pytest.fixture
def fake_dataframe() -> type[FakeDataFrame]:
    """Factory for creating fake DataFrames in options tests."""
    return FakeDataFrame


class DummyTicker:
    """Dummy ticker for options testing."""

    def __init__(self, options: list[str] | None = None, info: dict[str, Any] | None = None, option_chain=None):
        self.options = options or []
        self.info = info or {}
        self._option_chain = option_chain

    def option_chain(self, date: str | None = None):
        return self._option_chain


@pytest.fixture
def dummy_ticker() -> type[DummyTicker]:
    """Factory for creating dummy tickers in options tests."""
    return DummyTicker


class DummyOptionChain:
    """Dummy option chain for options testing."""

    def __init__(self, calls=None, puts=None, underlying: dict[str, Any] | None = None):
        self.calls = calls if calls is not None else FakeDataFrame()
        self.puts = puts if puts is not None else FakeDataFrame()
        self.underlying = underlying or {}


@pytest.fixture
def dummy_option_chain() -> type[DummyOptionChain]:
    """Factory for creating dummy option chains in options tests."""
    return DummyOptionChain


@pytest.fixture
def options_repository() -> YFinanceOptionsRepository:
    return YFinanceOptionsRepository()


@pytest.fixture
def financials_repository() -> YFinanceFinancialsRepository:
    return YFinanceFinancialsRepository()


@pytest.fixture
def holdings_repository() -> YFinanceHoldingsRepository:
    return YFinanceHoldingsRepository()


@pytest.fixture
def technical_analysis_repository() -> YFinanceTechnicalAnalysisRepository:
    return YFinanceTechnicalAnalysisRepository()


@pytest.fixture
def analysis_repository() -> YFinanceAnalysisRepository:
    return YFinanceAnalysisRepository()


@pytest.fixture
def crypto_repository() -> YFinanceCryptoRepository:
    return YFinanceCryptoRepository()


@pytest.fixture
def funds_repository() -> YFinanceFundsRepository:
    return YFinanceFundsRepository()


@pytest.fixture
def markets_repository() -> YFinanceMarketsRepository:
    return YFinanceMarketsRepository()


@pytest.fixture
def sector_industry_repository() -> YFinanceSectorIndustryRepository:
    return YFinanceSectorIndustryRepository()


@pytest.fixture
def stock_fast_info_payload() -> dict[str, Any]:
    return {
        "currency": "USD",
        "dayHigh": 150.0,
        "dayLow": 145.0,
        "exchange": "NASDAQ",
        "fiftyDayAverage": 148.0,
        "lastPrice": 149.0,
        "lastVolume": 1000000,
        "marketCap": 2000000000,
        "open": 146.0,
        "previousClose": 147.0,
        "quoteType": "equity",
        "regularMarketPreviousClose": 147.0,
        "shares": 10000000,
        "tenDayAverageVolume": 900000,
        "threeMonthAverageVolume": 950000,
        "timezone": "EST",
        "twoHundredDayAverage": 140.0,
        "yearChange": 0.1,
        "yearHigh": 155.0,
        "yearLow": 130.0,
    }
