"""Unit tests for YFinanceStockRepository."""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pandas as pd
import pytest
from pydantic import BaseModel

from openmarkets.schemas.stock import (
    CorporateActions,
    NewsItem,
    StockDividends,
    StockFastInfo,
    StockHistory,
    StockInfo,
    StockSplit,
    ValuationMeasuresEntry,
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


def test_get_history_with_datetime_column_intraday(stock_repository, stock_ticker, patch_yf, ohlcv_history_factory):
    """Test that get_history handles 'Datetime' column from intraday data."""
    dataframe = ohlcv_history_factory(
        [
            {
                "Datetime": datetime(2023, 1, 1, 9, 30),
                "Open": 100.0,
                "High": 110.0,
                "Low": 90.0,
                "Close": 105.0,
                "Volume": 1000,
                "Dividends": 0.0,
                "Stock Splits": 0.0,
            }
        ]
    )

    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            pass

        def history(self, period="1d", interval="1m") -> pd.DataFrame:
            return dataframe

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    result = stock_repository.get_history(stock_ticker, period="1d", interval="1m")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], StockHistory)
    assert result[0].open == 100.0
    assert result[0].date.year == 2023


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
    ("method_name", "info_payload", "expected_field", "expected_value"),
    [
        ("get_financial_summary", {"totalRevenue": 100, "revenueGrowth": 0.1}, "total_revenue", 100),
        ("get_risk_metrics", {"auditRisk": 1, "boardRisk": 2}, "audit_risk", 1),
        ("get_dividend_summary", {"dividendRate": 1.5, "dividendYield": 0.02}, "dividend_rate", 1.5),
        ("get_price_target", {"targetHighPrice": 200.0, "targetLowPrice": 150.0}, "target_high_price", 200.0),
        (
            "get_extended_financial_summary",
            {"marketCap": 1_000_000_000, "enterpriseValue": 900_000_000},
            "market_cap",
            1_000_000_000,
        ),
        ("get_quick_technical_indicators", {"currentPrice": 150.0, "fiftyDayAverage": 148.0}, "current_price", 150.0),
    ],
)
def test_info_based_methods_return_typed_models(
    stock_repository, stock_ticker, patch_yf, method_name, info_payload, expected_field, expected_value
):
    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            self.info = info_payload

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    method = getattr(stock_repository, method_name)
    result = method(stock_ticker)

    # A typed model, not a bare dict, so the tool exposes an output schema.
    assert isinstance(result, BaseModel)
    assert getattr(result, expected_field) == expected_value


def test_get_history_invalid_period_raises(stock_repository, stock_ticker):
    with pytest.raises(ValueError, match="Invalid period"):
        stock_repository.get_history(stock_ticker, period="invalid")


def test_get_history_invalid_interval_raises(stock_repository, stock_ticker):
    with pytest.raises(ValueError, match="Invalid interval"):
        stock_repository.get_history(stock_ticker, interval="invalid")


def test_get_valuation_history_transposes_periods_to_records(stock_repository, stock_ticker, patch_yf):
    """yfinance returns metrics as rows and periods as columns; the
    repository must transpose that into one record per period."""
    df = pd.DataFrame(
        {
            "Current": [100.0, 20.5],
            "6/30/2026": [90.0, 18.0],
        },
        index=["Market Cap", "Trailing P/E"],
    )

    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            pass

        def get_valuation_measures(self, freq="quarterly", periods=5):
            return df

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    result = stock_repository.get_valuation_history(stock_ticker)

    assert len(result) == 2
    assert all(isinstance(entry, ValuationMeasuresEntry) for entry in result)
    assert result[0].period == "Current"
    assert result[0].market_cap == 100.0
    assert result[0].trailing_pe == 20.5
    assert result[1].period == "6/30/2026"
    assert result[1].market_cap == 90.0


def test_get_valuation_history_empty_for_unsupported_instrument(stock_repository, stock_ticker, patch_yf):
    """Valuation measures do not apply to some instruments (e.g.
    cryptocurrencies); yfinance returns an empty DataFrame, and this must
    become an empty list rather than a construction error."""

    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            pass

        def get_valuation_measures(self, freq="quarterly", periods=5):
            return pd.DataFrame()

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    result = stock_repository.get_valuation_history(stock_ticker)

    assert result == []


def test_get_valuation_history_normalizes_nan_metrics_to_none(stock_repository, stock_ticker, patch_yf):
    """A company without 5-year growth estimates legitimately has no PEG
    ratio; yfinance represents that gap as float NaN, which must become
    None rather than the invalid JSON literal NaN."""
    df = pd.DataFrame(
        {"Current": [float("nan")]},
        index=["PEG Ratio (5yr expected)"],
    )

    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            pass

        def get_valuation_measures(self, freq="quarterly", periods=5):
            return df

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    result = stock_repository.get_valuation_history(stock_ticker)

    assert result[0].peg_ratio is None


def test_get_valuation_history_forwards_freq_and_periods(stock_repository, stock_ticker, patch_yf):
    """freq and periods must actually reach yfinance, not be silently
    dropped."""
    captured = {}

    class FakeTicker:
        def __init__(self, ticker: str, session=None):
            pass

        def get_valuation_measures(self, freq="quarterly", periods=5):
            captured["freq"] = freq
            captured["periods"] = periods
            return pd.DataFrame()

    patch_yf("openmarkets.repositories.stock", SimpleNamespace(Ticker=FakeTicker))

    stock_repository.get_valuation_history(stock_ticker, freq="yearly", periods=2)

    assert captured == {"freq": "yearly", "periods": 2}
