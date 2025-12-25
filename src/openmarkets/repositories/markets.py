"""Repository layer for market data operations.

Provides abstractions and implementations for fetching market summaries,
market status, and related market-level information.
"""

from abc import ABC, abstractmethod

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.schemas.markets import MarketStatus, MarketSummary, SummaryEntry


class IMarketsRepository(ABC):
    """Abstract interface for market data repositories."""

    @abstractmethod
    def get_market_summary(self, market: str, session: Session | None = None) -> MarketSummary:
        """Retrieve market summary data.

        Args:
            market: Market identifier.
            session: Optional HTTP session for request handling.

        Returns:
            Market summary data.
        """
        pass

    @abstractmethod
    def get_market_status(self, market: str, session: Session | None = None) -> MarketStatus:
        """Retrieve market status information.

        Args:
            market: Market identifier.
            session: Optional HTTP session for request handling.

        Returns:
            Market status data.
        """
        pass


class YFinanceMarketsRepository(IMarketsRepository):
    """Repository for accessing market data from yfinance.

    Infrastructure layer: encapsulates yfinance dependency.
    """

    def get_market_summary(self, market: str, session: Session | None = None) -> MarketSummary:
        """Retrieve market summary data.

        Args:
            market: Market identifier.
            session: Optional HTTP session for request handling.

        Returns:
            Market summary data.
        """
        market_obj = yf.Market(market, session=session)
        summary = market_obj.summary
        return MarketSummary(summary={k: SummaryEntry(**v) for k, v in summary.items()})

    def get_market_status(self, market: str, session: Session | None = None) -> MarketStatus:
        """Retrieve market status information.

        Args:
            market: Market identifier.
            session: Optional HTTP session for request handling.

        Returns:
            Market status data.
        """
        market_obj = yf.Market(market, session=session)
        status = market_obj.status
        return MarketStatus(**status)
