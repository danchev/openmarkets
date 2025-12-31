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
