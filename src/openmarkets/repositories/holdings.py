"""Repository layer for holdings data operations.

Provides abstractions and implementations for fetching institutional holdings,
mutual fund holdings, insider data, and major holders information.
"""

from abc import ABC, abstractmethod

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.schemas.holdings import (
    InsiderPurchase,
    InsiderRosterHolder,
    StockInstitutionalHoldings,
    StockMajorHolders,
    StockMutualFundHoldings,
)


class IHoldingsRepository(ABC):
    """Abstract interface for holdings data repositories."""

    """Abstract interface for holdings data repositories."""

    @abstractmethod
    def get_major_holders(self, ticker: str, session: Session | None = None) -> list[StockMajorHolders]:
        """Retrieve major holders information for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of major holders data.
        """
        pass

    @abstractmethod
    def get_institutional_holdings(
        self, ticker: str, session: Session | None = None
    ) -> list[StockInstitutionalHoldings]:
        """Retrieve institutional holdings for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of institutional holdings.
        """
        pass

    @abstractmethod
    def get_mutual_fund_holdings(self, ticker: str, session: Session | None = None) -> list[StockMutualFundHoldings]:
        """Retrieve mutual fund holdings for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of mutual fund holdings.
        """
        pass

    @abstractmethod
    def get_insider_purchases(self, ticker: str, session: Session | None = None) -> list[InsiderPurchase]:
        """Retrieve insider purchase transactions for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of insider purchases.
        """
        pass

    @abstractmethod
    def get_insider_roster_holders(self, ticker: str, session: Session | None = None) -> list[InsiderRosterHolder]:
        """Retrieve insider roster holders for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of insider roster holders.
        """
        pass


class YFinanceHoldingsRepository(IHoldingsRepository):
    """Repository for accessing holdings data from yfinance."""

    def get_major_holders(self, ticker: str, session: Session | None = None) -> list[StockMajorHolders]:
        """Retrieve major holders information for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of major holders data.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        df = ticker_obj.get_major_holders()
        transposed = df.transpose()
        reset_df = transposed.reset_index()
        records = reset_df.to_dict(orient="records")
        return [StockMajorHolders(**row) for row in records]

    def get_institutional_holdings(
        self, ticker: str, session: Session | None = None
    ) -> list[StockInstitutionalHoldings]:
        """Retrieve institutional holdings for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of institutional holdings.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        df = ticker_obj.get_institutional_holders()
        df.reset_index(inplace=True)
        return [StockInstitutionalHoldings(**row.to_dict()) for _, row in df.iterrows()]

    def get_mutual_fund_holdings(self, ticker: str, session: Session | None = None) -> list[StockMutualFundHoldings]:
        """Retrieve mutual fund holdings for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of mutual fund holdings.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        df = ticker_obj.get_mutualfund_holders()
        df.reset_index(inplace=True)
        return [StockMutualFundHoldings(**row.to_dict()) for _, row in df.iterrows()]

    def get_insider_purchases(self, ticker: str, session: Session | None = None) -> list[InsiderPurchase]:
        """Retrieve insider purchase transactions for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of insider purchases.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        df = ticker_obj.get_insider_purchases()
        df.reset_index(inplace=True)
        return [InsiderPurchase(**row.to_dict()) for _, row in df.iterrows()]

    def get_insider_roster_holders(self, ticker: str, session: Session | None = None) -> list[InsiderRosterHolder]:
        """Retrieve insider roster holders for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of insider roster holders.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        df = ticker_obj.get_insider_roster_holders()
        reset_df = df.reset_index()
        return [InsiderRosterHolder(**row.to_dict()) for _, row in reset_df.iterrows()]
