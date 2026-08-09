"""Repository layer for financial data operations.

Provides abstractions and implementations for fetching balance sheets,
income statements, cash flow statements, and other financial data.
"""

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.schemas.financials import (
    BalanceSheetEntry,
    CuratedFinancialSummary,
    EPSHistoryEntry,
    FinancialCalendar,
    IncomeStatementEntry,
    SecFilingRecord,
    TTMCashFlowStatementEntry,
    TTMIncomeStatementEntry,
)


class YFinanceFinancialsRepository:
    """Repository for accessing financial data from yfinance."""

    def get_curated_financials(self, ticker: str, session: Session | None = None) -> CuratedFinancialSummary:
        """Retrieve curated financial performance and solvency snapshot.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            CuratedFinancialSummary with 15 core financial metrics.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        info = ticker_obj.info or {}
        return CuratedFinancialSummary(
            symbol=info.get("symbol", ticker),
            total_revenue=info.get("totalRevenue"),
            gross_profit=info.get("grossProfits"),
            operating_income=info.get("operatingIncome") or info.get("ebitda"),
            net_income=info.get("netIncomeToCommon"),
            ebitda=info.get("ebitda"),
            operating_cashflow=info.get("operatingCashflow"),
            free_cashflow=info.get("freeCashflow"),
            total_cash=info.get("totalCash"),
            total_debt=info.get("totalDebt"),
            current_ratio=info.get("currentRatio"),
            debt_to_equity=info.get("debtToEquity"),
            gross_margin=info.get("grossMargins"),
            operating_margin=info.get("operatingMargins"),
            profit_margin=info.get("profitMargins"),
            return_on_equity=info.get("returnOnEquity"),
            return_on_assets=info.get("returnOnAssets"),
        )

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
        return [BalanceSheetEntry(**row) for row in reset_df.to_dict(orient="records")]

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
        return [IncomeStatementEntry(**row) for row in reset_df.to_dict(orient="records")]

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
        return [TTMIncomeStatementEntry(**row) for row in reset_data.to_dict(orient="records")]

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
        return [TTMCashFlowStatementEntry(**row) for row in reset_data.to_dict(orient="records")]

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
        return [EPSHistoryEntry(**row) for row in reset_df.to_dict(orient="records")]
