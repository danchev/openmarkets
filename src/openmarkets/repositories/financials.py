from abc import ABC, abstractmethod

import yfinance as yf

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
    def fetch_balance_sheet(self, ticker: str) -> list[BalanceSheetEntry]:
        pass

    @abstractmethod
    def fetch_income_statement(self, ticker: str) -> list[IncomeStatementEntry]:
        pass

    @abstractmethod
    def fetch_ttm_income_statement(self, ticker: str) -> list[TTMIncomeStatementEntry]:
        pass

    @abstractmethod
    def fetch_ttm_cash_flow_statement(self, ticker: str) -> list[TTMCashFlowStatementEntry]:
        pass

    @abstractmethod
    def fetch_financial_calendar(self, ticker: str) -> FinancialCalendar:
        pass

    @abstractmethod
    def fetch_sec_filings(self, ticker: str) -> list[SecFilingRecord]:
        pass

    @abstractmethod
    def fetch_eps_history(self, ticker: str) -> list[EPSHistoryEntry]:
        pass


class YFinanceFinancialsRepository(IFinancialsRepository):
    """
    Repository for accessing financial data from yfinance.
    """

    @staticmethod
    def fetch_balance_sheet(ticker: str) -> list[BalanceSheetEntry]:
        df = yf.Ticker(ticker).get_balance_sheet()
        return [BalanceSheetEntry(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]

    @staticmethod
    def fetch_income_statement(ticker: str) -> list[IncomeStatementEntry]:
        df = yf.Ticker(ticker).get_income_stmt()
        return [IncomeStatementEntry(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]

    @staticmethod
    def fetch_ttm_income_statement(ticker: str) -> list[TTMIncomeStatementEntry]:
        data = yf.Ticker(ticker).ttm_income_stmt
        return [TTMIncomeStatementEntry(**row.to_dict()) for _, row in data.transpose().reset_index().iterrows()]

    @staticmethod
    def fetch_ttm_cash_flow_statement(ticker: str) -> list[TTMCashFlowStatementEntry]:
        data = yf.Ticker(ticker).ttm_cash_flow
        return [TTMCashFlowStatementEntry(**row.to_dict()) for _, row in data.transpose().reset_index().iterrows()]

    @staticmethod
    def fetch_financial_calendar(ticker: str) -> FinancialCalendar:
        data = yf.Ticker(ticker).get_calendar()
        return FinancialCalendar(**data)

    @staticmethod
    def fetch_sec_filings(ticker: str) -> list[SecFilingRecord]:
        data = yf.Ticker(ticker).get_sec_filings()
        return [SecFilingRecord(**filing) for filing in data]

    @staticmethod
    def fetch_eps_history(ticker: str) -> list[EPSHistoryEntry]:
        df = yf.Ticker(ticker).get_earnings_dates()
        if df is None:
            return []
        return [EPSHistoryEntry(**row.to_dict()) for _, row in df.reset_index().iterrows()]
