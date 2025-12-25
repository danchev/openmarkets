"""Repository layer for financial data operations.

Provides abstractions and implementations for fetching balance sheets,
income statements, cash flow statements, and other financial data.
"""

from abc import ABC, abstractmethod

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.schemas.financials import (
    BalanceSheetEntry,
    EPSHistoryEntry,
    FinancialCalendar,
    IncomeStatementEntry,
    SecFilingRecord,
    TTMCashFlowStatementEntry,
    TTMIncomeStatementEntry,
)


class IFinancialsRepository(ABC):
    """Abstract interface for financial data repositories."""

    """Abstract interface for financial data repositories."""

    @abstractmethod
    def get_balance_sheet(self, ticker: str, session: Session | None = None) -> list[BalanceSheetEntry]:
        """Retrieve balance sheet data for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of balance sheet entries.
        """
        pass

    @abstractmethod
    def get_income_statement(self, ticker: str, session: Session | None = None) -> list[IncomeStatementEntry]:
        """Retrieve income statement data for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of income statement entries.
        """
        pass

    @abstractmethod
    def get_ttm_income_statement(self, ticker: str, session: Session | None = None) -> list[TTMIncomeStatementEntry]:
        """Retrieve trailing twelve months income statement for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of TTM income statement entries.
        """
        pass

    @abstractmethod
    def get_ttm_cash_flow_statement(
        self, ticker: str, session: Session | None = None
    ) -> list[TTMCashFlowStatementEntry]:
        """Retrieve trailing twelve months cash flow statement for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of TTM cash flow statement entries.
        """
        pass

    @abstractmethod
    def get_financial_calendar(self, ticker: str, session: Session | None = None) -> FinancialCalendar:
        """Retrieve financial calendar for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Financial calendar data.
        """
        pass

    @abstractmethod
    def get_sec_filings(self, ticker: str, session: Session | None = None) -> list[SecFilingRecord]:
        """Retrieve SEC filings for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of SEC filing records.
        """
        pass

    @abstractmethod
    def get_eps_history(self, ticker: str, session: Session | None = None) -> list[EPSHistoryEntry]:
        """Retrieve EPS history for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of EPS history entries.
        """
        pass


class YFinanceFinancialsRepository(IFinancialsRepository):
    """Repository for accessing financial data from yfinance."""

    def get_balance_sheet(self, ticker: str, session: Session | None = None) -> list[BalanceSheetEntry]:
        """Retrieve balance sheet data for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of balance sheet entries.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        df = ticker_obj.get_balance_sheet()
        transposed = df.transpose()
        reset_df = transposed.reset_index()
        return [BalanceSheetEntry(**row.to_dict()) for _, row in reset_df.iterrows()]

    def get_income_statement(self, ticker: str, session: Session | None = None) -> list[IncomeStatementEntry]:
        """Retrieve income statement data for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of income statement entries.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        df = ticker_obj.get_income_stmt()
        transposed = df.transpose()
        reset_df = transposed.reset_index()
        return [IncomeStatementEntry(**row.to_dict()) for _, row in reset_df.iterrows()]

    def get_ttm_income_statement(self, ticker: str, session: Session | None = None) -> list[TTMIncomeStatementEntry]:
        """Retrieve trailing twelve months income statement for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of TTM income statement entries.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        data = ticker_obj.ttm_income_stmt
        transposed = data.transpose()
        reset_data = transposed.reset_index()
        return [TTMIncomeStatementEntry(**row.to_dict()) for _, row in reset_data.iterrows()]

    def get_ttm_cash_flow_statement(
        self, ticker: str, session: Session | None = None
    ) -> list[TTMCashFlowStatementEntry]:
        """Retrieve trailing twelve months cash flow statement for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of TTM cash flow statement entries.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        data = ticker_obj.ttm_cash_flow
        transposed = data.transpose()
        reset_data = transposed.reset_index()
        return [TTMCashFlowStatementEntry(**row.to_dict()) for _, row in reset_data.iterrows()]

    def get_financial_calendar(self, ticker: str, session: Session | None = None) -> FinancialCalendar:
        """Retrieve financial calendar for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Financial calendar data.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        data = ticker_obj.get_calendar()
        return FinancialCalendar(**data)

    def get_sec_filings(self, ticker: str, session: Session | None = None) -> list[SecFilingRecord]:
        """Retrieve SEC filings for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of SEC filing records.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        data = ticker_obj.get_sec_filings()
        return [SecFilingRecord(**filing) for filing in data]

    def get_eps_history(self, ticker: str, session: Session | None = None) -> list[EPSHistoryEntry]:
        """Retrieve EPS history for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of EPS history entries.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        df = ticker_obj.get_earnings_dates()
        if df is None:
            return []
        reset_df = df.reset_index()
        return [EPSHistoryEntry(**row.to_dict()) for _, row in reset_df.iterrows()]
