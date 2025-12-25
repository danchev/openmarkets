from abc import ABC, abstractmethod

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.schemas.markets import MarketStatus, MarketSummary, SummaryEntry


class IMarketsRepository(ABC):
    @abstractmethod
    def get_market_summary(self, market: str, session: Session | None = None) -> MarketSummary:
        pass

    @abstractmethod
    def get_market_status(self, market: str, session: Session | None = None) -> MarketStatus:
        pass


class YFinanceMarketsRepository(IMarketsRepository):
    """
    Repository for accessing market data from external sources (e.g., yfinance).
    Infrastructure layer: encapsulates yfinance dependency.
    """

    def get_market_summary(self, market: str, session: Session | None = None) -> MarketSummary:
        """Fetch raw market summary data from yfinance."""
        summary = yf.Market(market, session=session).summary
        return MarketSummary(summary={k: SummaryEntry(**v) for k, v in summary.items()})

    def get_market_status(self, market: str, session: Session | None = None) -> MarketStatus:
        """Fetch raw market status data from yfinance."""
        status = yf.Market(market, session=session).status
        return MarketStatus(**status)
