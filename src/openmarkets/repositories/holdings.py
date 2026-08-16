"""Repository layer for holdings data operations.

Provides abstractions and implementations for fetching institutional holdings,
mutual fund holdings, insider data, and major holders information.
"""

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.core.provider import dataframe_records
from openmarkets.schemas.holdings import (
    InsiderPurchase,
    InsiderRosterHolder,
    StockInstitutionalHoldings,
    StockMajorHolders,
    StockMutualFundHoldings,
)


class YFinanceHoldingsRepository:
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
        records = dataframe_records(ticker_obj.get_major_holders(), f"major holders for {ticker}", transpose=True)
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
        records = dataframe_records(ticker_obj.get_institutional_holders(), f"institutional holders for {ticker}")
        return [StockInstitutionalHoldings(**row) for row in records]

    def get_mutual_fund_holdings(self, ticker: str, session: Session | None = None) -> list[StockMutualFundHoldings]:
        """Retrieve mutual fund holdings for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of mutual fund holdings.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        records = dataframe_records(ticker_obj.get_mutualfund_holders(), f"mutual-fund holders for {ticker}")
        return [StockMutualFundHoldings(**row) for row in records]

    def get_insider_purchases(self, ticker: str, session: Session | None = None) -> list[InsiderPurchase]:
        """Retrieve insider purchase transactions for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of insider purchases.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        records = dataframe_records(ticker_obj.get_insider_purchases(), f"insider purchases for {ticker}")
        return [InsiderPurchase(**row) for row in records]

    def get_insider_roster_holders(self, ticker: str, session: Session | None = None) -> list[InsiderRosterHolder]:
        """Retrieve insider roster holders for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of insider roster holders.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        records = dataframe_records(ticker_obj.get_insider_roster_holders(), f"insider roster for {ticker}")
        return [InsiderRosterHolder(**row) for row in records]
