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


def fetch_balance_sheet(ticker: str) -> list[BalanceSheetEntry]:
    """
    Fetch balance sheet data for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[BalanceSheetEntry]: List of balance sheet entries.
    """
    df = yf.Ticker(ticker).get_balance_sheet()
    return [BalanceSheetEntry(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]


def fetch_income_statement(ticker: str) -> list[IncomeStatementEntry]:
    """
    Fetch income statement data for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[IncomeStatementEntry]: List of income statement entries.
    """
    df = yf.Ticker(ticker).get_income_stmt()
    return [IncomeStatementEntry(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]


def fetch_ttm_income_statement(ticker: str) -> list[TTMIncomeStatementEntry]:
    """
    Fetch TTM income statement data for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[TTMIncomeStatementEntry]: List of TTM income statement entries.
    """
    data = yf.Ticker(ticker).ttm_income_stmt
    return [TTMIncomeStatementEntry(**row.to_dict()) for _, row in data.transpose().reset_index().iterrows()]


def fetch_ttm_cash_flow_statement(ticker: str) -> list[TTMCashFlowStatementEntry]:
    """
    Fetch TTM cash flow statement data for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[TTMCashFlowStatementEntry]: List of TTM cash flow statement entries.
    """
    data = yf.Ticker(ticker).ttm_cash_flow
    return [TTMCashFlowStatementEntry(**row.to_dict()) for _, row in data.transpose().reset_index().iterrows()]


def fetch_financial_calendar(ticker: str) -> FinancialCalendar:
    """
    Fetch financial calendar data for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        FinancialCalendar: Financial calendar data.
    """
    data = yf.Ticker(ticker).get_calendar()
    return FinancialCalendar(**data)


def fetch_sec_filings(ticker: str) -> list[SecFilingRecord]:
    """
    Fetch SEC filings for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[SecFilingRecord]: List of SEC filing records.
    """
    data = yf.Ticker(ticker).get_sec_filings()
    return [SecFilingRecord(**filing) for filing in data]


def fetch_eps_history(ticker: str) -> list[EPSHistoryEntry]:
    """
    Fetch EPS history for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[EPSHistoryEntry]: List of EPS history entries.
    """
    df = yf.Ticker(ticker).get_earnings_dates()
    if df is None:
        return []
    return [EPSHistoryEntry(**row.to_dict()) for _, row in df.reset_index().iterrows()]
