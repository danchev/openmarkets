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


def get_balance_sheet_for_ticker(ticker: str) -> list[BalanceSheetEntry]:
    """
    Fetch balance sheet data for a given ticker and return as a list of BalanceSheetEntry.
    """
    df = yf.Ticker(ticker).get_balance_sheet()
    return [BalanceSheetEntry(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]


def get_income_statement_for_ticker(ticker: str) -> list[IncomeStatementEntry]:
    """
    Fetch income statement data for a given ticker and return as a list of IncomeStatementEntry.
    """
    df = yf.Ticker(ticker).get_income_stmt()
    return [IncomeStatementEntry(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]


def get_ttm_income_statement_for_ticker(ticker: str) -> list[TTMIncomeStatementEntry]:
    """
    Fetch TTM income statement data for a given ticker and return as TTMIncomeStatementEntry.
    """
    data = yf.Ticker(ticker).ttm_income_stmt
    return [TTMIncomeStatementEntry(**row.to_dict()) for _, row in data.transpose().reset_index().iterrows()]


def get_ttm_cash_flow_statement_for_ticker(ticker: str) -> list[TTMCashFlowStatementEntry]:
    """
    Fetch TTM cash flow statement data for a given ticker and return as TTMCashFlowStatementEntry.
    """
    data = yf.Ticker(ticker).ttm_cash_flow
    return [TTMCashFlowStatementEntry(**row.to_dict()) for _, row in data.transpose().reset_index().iterrows()]


def get_financial_calendar_for_ticker(ticker: str) -> FinancialCalendar:
    """
    Fetch financial calendar data for a given ticker and return as FinancialCalendar.
    """
    data = yf.Ticker(ticker).get_calendar()
    return FinancialCalendar(**data)


def get_sec_filings_for_ticker(ticker: str) -> list[SecFilingRecord]:
    """
    Fetch SEC filings for a given ticker and return as a list of SecFilingRecord.
    """
    data = yf.Ticker(ticker).get_sec_filings()
    return [SecFilingRecord(**filing) for filing in data]


def get_eps_history_for_ticker(ticker: str) -> list[EPSHistoryEntry]:
    """
    Fetch EPS history for a given ticker and return as a list of EPSHistoryEntry.
    """
    df = yf.Ticker(ticker).get_earnings_dates()
    return [EPSHistoryEntry(**row.to_dict()) for _, row in df.reset_index().iterrows()]
