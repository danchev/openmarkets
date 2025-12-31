"""Shared fixtures for root-level legacy tests."""

from types import SimpleNamespace
from typing import Any, Callable

import pytest


@pytest.fixture
def patch_yf(monkeypatch: pytest.MonkeyPatch) -> Callable[[type], None]:
    """Patch yfinance module with custom Ticker class."""

    def _patch(ticker_class: type) -> None:
        yf_mock = type("YFinance", (), {"Ticker": ticker_class})
        monkeypatch.setattr("yfinance", yf_mock)

    return _patch


@pytest.fixture
def make_ticker_factory(monkeypatch: pytest.MonkeyPatch) -> Callable[[dict[str, Any]], type]:
    """Create a factory for building Ticker mock classes."""

    def _factory(attributes: dict[str, Any]) -> type:
        """Build Ticker class with specified attributes."""

        class TickerMock:
            def __init__(self, ticker: str, session: Any = None):
                for key, value in attributes.items():
                    setattr(self, key, value)

        return TickerMock

    return _factory


@pytest.fixture
def patch_yf_with_attributes(
    monkeypatch: pytest.MonkeyPatch, make_ticker_factory: Callable[[dict[str, Any]], type]
) -> Callable[[str, dict[str, Any]], None]:
    """Patch yfinance module with Ticker having specified attributes."""

    def _patch(module_path: str, attributes: dict[str, Any]) -> None:
        ticker_class = make_ticker_factory(attributes)
        yf_mock = type("YFinance", (), {"Ticker": ticker_class})
        monkeypatch.setattr(module_path, yf_mock)

    return _patch


class FakeDataFrame:
    """Fake DataFrame for tests that don't need full pandas functionality."""

    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def reset_index(self) -> "FakeDataFrame":
        return self

    def transpose(self) -> "FakeDataFrame":
        return self

    def iterrows(self):
        """Yield (index, row) tuples where row has to_dict() method."""
        for i, row_data in enumerate(self._rows):
            row = SimpleNamespace(to_dict=lambda data=row_data: data)
            yield i, row


@pytest.fixture
def fake_dataframe() -> type[FakeDataFrame]:
    """Factory for creating fake DataFrames in tests."""
    return FakeDataFrame
