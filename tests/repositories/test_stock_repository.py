"""Unit tests for YFinanceStockRepository."""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pandas as pd
import pytest

from openmarkets.schemas.stock import (
    CorporateActions,
    NewsItem,
    StockDividends,
    StockFastInfo,
    StockHistory,
    StockInfo,
    StockSplit,
)


def test_get_fast_info_returns_model(stock_repository, stock_ticker, patch_yf, stock_fast_info_payload):
    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            self.fast_info = stock_fast_info_payload

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    result = stock_repository.get_fast_info(stock_ticker)
    assert isinstance(result, StockFastInfo)
    assert result.currency == "USD"


def test_get_info_returns_model(stock_repository, stock_ticker, patch_yf):
    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            self.info = {"currency": "USD", "marketCap": 2_000_000_000}

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    result = stock_repository.get_info(stock_ticker)
    assert isinstance(result, StockInfo)
    assert result.currency == "USD"


def test_get_history_returns_models(stock_repository, stock_ticker, patch_yf, ohlcv_history_factory):
    dataframe = ohlcv_history_factory(
        [
            {
                "Date": datetime(2023, 1, 1),
                "Open": 100.0,
                "High": 110.0,
                "Low": 90.0,
                "Close": 105.0,
                "Volume": 1000,
                "Dividends": 0.5,
                "Stock Splits": 0,
            }
        ]
    )

    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            pass

        def history(self, period="1y", interval="1d") -> pd.DataFrame:
            return dataframe

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    result = stock_repository.get_history(stock_ticker)
    assert isinstance(result, list)
    assert isinstance(result[0], StockHistory)


def test_get_dividends_returns_models(stock_repository, stock_ticker, patch_yf):
    class FakeDividends:
        def to_dict(self):
            return {"2023-01-01": 0.5}

    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            self.dividends = FakeDividends()

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    result = stock_repository.get_dividends(stock_ticker)
    assert isinstance(result, list)
    assert isinstance(result[0], StockDividends)


def test_get_splits_returns_models(stock_repository, stock_ticker, patch_yf):
    class FakeSplits:
        def items(self):
            return [("2023-01-01", 2)]

    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            self.splits = FakeSplits()

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    result = stock_repository.get_splits(stock_ticker)
    assert isinstance(result, list)
    assert isinstance(result[0], StockSplit)


def test_get_news_returns_models(stock_repository, stock_ticker, patch_yf):
    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            self.news = [{"id": "news1", "content": {"title": "News Title", "link": "http://example.com"}}]

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    result = stock_repository.get_news(stock_ticker)
    assert isinstance(result, list)
    assert isinstance(result[0], NewsItem)


def test_get_corporate_actions_returns_models(stock_repository, stock_ticker, patch_yf):
    class FakeActions:
        def reset_index(self):
            return self

        def iterrows(self):
            yield 0, SimpleNamespace(to_dict=lambda: {"Date": "2023-01-01", "Dividends": 0.5, "Stock Splits": 2.0})

    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            self.actions = FakeActions()

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    result = stock_repository.get_corporate_actions(stock_ticker)
    assert isinstance(result, list)
    assert isinstance(result[0], CorporateActions)


@pytest.mark.parametrize(
    ("method_name", "info_payload", "expected_key"),
    [
        ("get_financial_summary", {"totalRevenue": 100, "revenueGrowth": 0.1}, "totalRevenue"),
        ("get_risk_metrics", {"auditRisk": 1, "boardRisk": 2}, "auditRisk"),
        ("get_dividend_summary", {"dividendRate": 1.5, "dividendYield": 0.02}, "dividendRate"),
        ("get_price_target", {"targetHighPrice": 200.0, "targetLowPrice": 150.0}, "targetHighPrice"),
        ("get_financial_summary_v2", {"marketCap": 1_000_000_000, "enterpriseValue": 900_000_000}, "marketCap"),
        ("get_quick_technical_indicators", {"currentPrice": 150.0, "fiftyDayAverage": 148.0}, "currentPrice"),
    ],
)
def test_info_based_methods_return_dicts(
    stock_repository, stock_ticker, patch_yf, method_name, info_payload, expected_key
):
    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            self.info = info_payload

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    method = getattr(stock_repository, method_name)
    result = method(stock_ticker)
    assert isinstance(result, dict)
    assert expected_key in result


def test_get_history_invalid_period_raises(stock_repository, stock_ticker):
    with pytest.raises(ValueError, match="Invalid period"):
        stock_repository.get_history(stock_ticker, period="invalid")


def test_get_history_invalid_interval_raises(stock_repository, stock_ticker):
    with pytest.raises(ValueError, match="Invalid interval"):
        stock_repository.get_history(stock_ticker, interval="invalid")
