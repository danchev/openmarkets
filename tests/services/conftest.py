from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import cast

import pandas as pd
import pytest
from curl_cffi.requests import Session

from openmarkets.repositories.stock import IStockRepository
from openmarkets.services.stock import StockService
from openmarkets.services.utils import ToolRegistrationMixin


class StockRepositorySpy(IStockRepository):
    """A minimal spy for StockService delegation tests."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def get_fast_info(self, ticker: str, session: Session | None = None):
        self.calls.append(("get_fast_info", ticker, session))
        return {"symbol": ticker}

    def get_info(self, ticker: str, session: Session | None = None):
        self.calls.append(("get_info", ticker, session))
        return {"symbol": ticker}

    def get_history(self, ticker: str, period: str = "1y", interval: str = "1d", session: Session | None = None):
        self.calls.append(("get_history", ticker, period, interval, session))
        return []

    def get_dividends(self, ticker: str, session: Session | None = None):
        self.calls.append(("get_dividends", ticker, session))
        return []

    def get_financial_summary(self, ticker: str, session: Session | None = None) -> dict:
        self.calls.append(("get_financial_summary", ticker, session))
        return {}

    def get_risk_metrics(self, ticker: str, session: Session | None = None) -> dict:
        self.calls.append(("get_risk_metrics", ticker, session))
        return {}

    def get_dividend_summary(self, ticker: str, session: Session | None = None) -> dict:
        self.calls.append(("get_dividend_summary", ticker, session))
        return {}

    def get_price_target(self, ticker: str, session: Session | None = None) -> dict:
        self.calls.append(("get_price_target", ticker, session))
        return {}

    def get_financial_summary_v2(self, ticker: str, session: Session | None = None) -> dict:
        self.calls.append(("get_financial_summary_v2", ticker, session))
        return {}

    def get_quick_technical_indicators(self, ticker: str, session: Session | None = None) -> dict:
        self.calls.append(("get_quick_technical_indicators", ticker, session))
        return {}

    def get_splits(self, ticker: str, session: Session | None = None):
        self.calls.append(("get_splits", ticker, session))
        return []

    def get_corporate_actions(self, ticker: str, session: Session | None = None):
        self.calls.append(("get_corporate_actions", ticker, session))
        return []

    def get_news(self, ticker: str, session: Session | None = None):
        self.calls.append(("get_news", ticker, session))
        return []


class McpToolRegistrySpy:
    """Captures functions decorated via mcp.tool()."""

    def __init__(self) -> None:
        self.registered: list[str] = []

    def tool(self):
        def decorator(func):
            self.registered.append(func.__name__)
            return func

        return decorator


class ToolRegistrationService(ToolRegistrationMixin):
    def public(self) -> str:
        return "ok"

    @staticmethod
    def static_method() -> str:
        return "static"

    @classmethod
    def class_method(cls) -> str:
        return "class"

    @property
    def property_method(self) -> str:
        return "property"

    def _private(self) -> str:
        return "no"


@pytest.fixture
def stock_repository_spy() -> StockRepositorySpy:
    return StockRepositorySpy()


@pytest.fixture
def stock_service(stock_repository_spy: StockRepositorySpy) -> StockService:
    session_sentinel = cast(Session, object())
    return StockService(repository=stock_repository_spy, session=session_sentinel)


@pytest.fixture
def mcp_tool_registry_spy() -> McpToolRegistrySpy:
    return McpToolRegistrySpy()


@pytest.fixture
def tool_registration_service() -> ToolRegistrationService:
    return ToolRegistrationService()


@pytest.fixture
def hist_factory() -> Callable[
    [Iterable[float], Iterable[float] | None, Iterable[float] | None, Iterable[int] | None], pd.DataFrame
]:
    def _make(
        close_values: Iterable[float],
        high_values: Iterable[float] | None = None,
        low_values: Iterable[float] | None = None,
        volume_values: Iterable[int] | None = None,
    ) -> pd.DataFrame:
        dataframe = pd.DataFrame()
        dataframe["Close"] = list(close_values)
        dataframe["High"] = list(high_values) if high_values is not None else dataframe["Close"]
        dataframe["Low"] = list(low_values) if low_values is not None else dataframe["Close"]
        dataframe["Volume"] = list(volume_values) if volume_values is not None else [1] * len(dataframe["Close"])
        return dataframe

    return _make
