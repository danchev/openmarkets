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
    @abstractmethod
    def get_balance_sheet(self, ticker: str, session: Session | None = None) -> list[BalanceSheetEntry]:
        pass

    @abstractmethod
    def get_income_statement(self, ticker: str, session: Session | None = None) -> list[IncomeStatementEntry]:
        pass

    @abstractmethod
    def get_ttm_income_statement(self, ticker: str, session: Session | None = None) -> list[TTMIncomeStatementEntry]:
        pass

    @abstractmethod
    def get_ttm_cash_flow_statement(
        self, ticker: str, session: Session | None = None
    ) -> list[TTMCashFlowStatementEntry]:
        pass

    @abstractmethod
    def get_financial_calendar(self, ticker: str, session: Session | None = None) -> FinancialCalendar:
        pass

    @abstractmethod
    def get_sec_filings(self, ticker: str, session: Session | None = None) -> list[SecFilingRecord]:
        pass

    @abstractmethod
    def get_eps_history(self, ticker: str, session: Session | None = None) -> list[EPSHistoryEntry]:
        pass


class YFinanceFinancialsRepository(IFinancialsRepository):
    """
    Repository for accessing financial data from yfinance.
    """

    def get_balance_sheet(self, ticker: str, session: Session | None = None) -> list[BalanceSheetEntry]:
        df = yf.Ticker(ticker, session=session).get_balance_sheet()
        return [BalanceSheetEntry(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]

    def get_income_statement(self, ticker: str, session: Session | None = None) -> list[IncomeStatementEntry]:
        df = yf.Ticker(ticker, session=session).get_income_stmt()
        return [IncomeStatementEntry(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]

    def get_ttm_income_statement(self, ticker: str, session: Session | None = None) -> list[TTMIncomeStatementEntry]:
        data = yf.Ticker(ticker, session=session).ttm_income_stmt
        return [TTMIncomeStatementEntry(**row.to_dict()) for _, row in data.transpose().reset_index().iterrows()]

    def get_ttm_cash_flow_statement(
        self, ticker: str, session: Session | None = None
    ) -> list[TTMCashFlowStatementEntry]:
        data = yf.Ticker(ticker, session=session).ttm_cash_flow
        return [TTMCashFlowStatementEntry(**row.to_dict()) for _, row in data.transpose().reset_index().iterrows()]

    def get_financial_calendar(self, ticker: str, session: Session | None = None) -> FinancialCalendar:
        data = yf.Ticker(ticker, session=session).get_calendar()
        return FinancialCalendar(**data)

    def get_sec_filings(self, ticker: str, session: Session | None = None) -> list[SecFilingRecord]:
        data = yf.Ticker(ticker, session=session).get_sec_filings()
        return [SecFilingRecord(**filing) for filing in data]

    def get_eps_history(self, ticker: str, session: Session | None = None) -> list[EPSHistoryEntry]:
        df = yf.Ticker(ticker, session=session).get_earnings_dates()
        if df is None:
            return []
        return [EPSHistoryEntry(**row.to_dict()) for _, row in df.reset_index().iterrows()]
