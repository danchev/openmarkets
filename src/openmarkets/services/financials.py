from typing import Annotated

from openmarkets.repositories.financials import IFinancialsRepository, YFinanceFinancialsRepository
from openmarkets.schemas.financials import (
    BalanceSheetEntry,
    EPSHistoryEntry,
    FinancialCalendar,
    IncomeStatementEntry,
    SecFilingRecord,
    TTMCashFlowStatementEntry,
    TTMIncomeStatementEntry,
)
from openmarkets.services.utils import ToolRegistrationMixin


class FinancialsService(ToolRegistrationMixin):
    """
    Service layer for financials business logic.
    Provides methods to retrieve various financial statements, calendars, filings, and EPS history for a given ticker.
    """

    def __init__(self, repository: IFinancialsRepository | None = None):
        """
        Initialize the FinancialsService with a repository dependency.

        Args:
            repository (IFinancialsRepository): The repository instance for data access.
        """
        self.repository = repository or YFinanceFinancialsRepository()

    def get_balance_sheet(self, ticker: Annotated[str, "The symbol of the security."]) -> list[BalanceSheetEntry]:
        """
        Retrieve the balance sheet for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[BalanceSheetEntry]: List of balance sheet entries.
        """
        return self.repository.fetch_balance_sheet(ticker)

    def get_income_statement(self, ticker: Annotated[str, "The symbol of the security."]) -> list[IncomeStatementEntry]:
        """
        Retrieve the income statement for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[IncomeStatementEntry]: List of income statement entries.
        """
        return self.repository.fetch_income_statement(ticker)

    def get_ttm_income_statement(
        self, ticker: Annotated[str, "The symbol of the security."]
    ) -> list[TTMIncomeStatementEntry]:
        """
        Retrieve the trailing twelve months (TTM) income statement for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[TTMIncomeStatementEntry]: List of TTM income statement entries.
        """
        return self.repository.fetch_ttm_income_statement(ticker)

    def get_ttm_cash_flow_statement(
        self, ticker: Annotated[str, "The symbol of the security."]
    ) -> list[TTMCashFlowStatementEntry]:
        """
        Retrieve the trailing twelve months (TTM) cash flow statement for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[TTMCashFlowStatementEntry]: List of TTM cash flow statement entries.
        """
        return self.repository.fetch_ttm_cash_flow_statement(ticker)

    def get_financial_calendar(self, ticker: Annotated[str, "The symbol of the security."]) -> FinancialCalendar:
        """
        Retrieve the financial calendar for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            FinancialCalendar: Financial calendar data.
        """
        return self.repository.fetch_financial_calendar(ticker)

    def get_sec_filings(self, ticker: Annotated[str, "The symbol of the security."]) -> list[SecFilingRecord]:
        """
        Retrieve SEC filings for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[SecFilingRecord]: List of SEC filing records.
        """
        return self.repository.fetch_sec_filings(ticker)

    def get_eps_history(self, ticker: Annotated[str, "The symbol of the security."]) -> list[EPSHistoryEntry]:
        """
        Retrieve EPS (Earnings Per Share) history for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[EPSHistoryEntry]: List of EPS history entries.
        """
        return self.repository.fetch_eps_history(ticker)

    def get_full_financials(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve a full set of financial data for a given ticker, aggregating all available financial statements and records.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            dict: Dictionary containing all financial data for the ticker.
        """
        return {
            "balance_sheet": self.repository.fetch_balance_sheet(ticker),
            "income_statement": self.repository.fetch_income_statement(ticker),
            "ttm_income_statement": self.repository.fetch_ttm_income_statement(ticker),
            "ttm_cash_flow_statement": self.repository.fetch_ttm_cash_flow_statement(ticker),
            "financial_calendar": self.repository.fetch_financial_calendar(ticker),
            "sec_filings": self.repository.fetch_sec_filings(ticker),
            "eps_history": self.repository.fetch_eps_history(ticker),
        }


financials_service = FinancialsService()
