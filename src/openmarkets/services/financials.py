from typing import Annotated

from curl_cffi.requests import Session

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

    def __init__(self, repository: IFinancialsRepository | None = None, session: None = None):
        """
        Initialize the FinancialsService with a repository dependency.

        Args:
            repository (IFinancialsRepository): The repository instance for data access.
        """
        self.repository = repository or YFinanceFinancialsRepository()
        self.session = session or Session(impersonate="chrome")

    def get_balance_sheet(self, ticker: Annotated[str, "The symbol of the security."]) -> list[BalanceSheetEntry]:
        """
        Retrieve the balance sheet for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[BalanceSheetEntry]: List of balance sheet entries.
        """
        return self.repository.get_balance_sheet(ticker, session=self.session)

    def get_income_statement(self, ticker: Annotated[str, "The symbol of the security."]) -> list[IncomeStatementEntry]:
        """
        Retrieve the income statement for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[IncomeStatementEntry]: List of income statement entries.
        """
        return self.repository.get_income_statement(ticker, session=self.session)

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
        return self.repository.get_ttm_income_statement(ticker, session=self.session)

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
        return self.repository.get_ttm_cash_flow_statement(ticker, session=self.session)

    def get_financial_calendar(self, ticker: Annotated[str, "The symbol of the security."]) -> FinancialCalendar:
        """
        Retrieve the financial calendar for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            FinancialCalendar: Financial calendar data.
        """
        return self.repository.get_financial_calendar(ticker, session=self.session)

    def get_sec_filings(self, ticker: Annotated[str, "The symbol of the security."]) -> list[SecFilingRecord]:
        """
        Retrieve SEC filings for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[SecFilingRecord]: List of SEC filing records.
        """
        return self.repository.get_sec_filings(ticker, session=self.session)

    def get_eps_history(self, ticker: Annotated[str, "The symbol of the security."]) -> list[EPSHistoryEntry]:
        """
        Retrieve EPS (Earnings Per Share) history for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[EPSHistoryEntry]: List of EPS history entries.
        """
        return self.repository.get_eps_history(ticker, session=self.session)

    def get_full_financials(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve a full set of financial data for a given ticker, aggregating all available financial statements and records.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            dict: Dictionary containing all financial data for the ticker.
        """
        return {
            "balance_sheet": self.repository.get_balance_sheet(ticker, session=self.session),
            "income_statement": self.repository.get_income_statement(ticker, session=self.session),
            "ttm_income_statement": self.repository.get_ttm_income_statement(ticker, session=self.session),
            "ttm_cash_flow_statement": self.repository.get_ttm_cash_flow_statement(ticker, session=self.session),
            "financial_calendar": self.repository.get_financial_calendar(ticker, session=self.session),
            "sec_filings": self.repository.get_sec_filings(ticker, session=self.session),
            "eps_history": self.repository.get_eps_history(ticker, session=self.session),
        }


financials_service = FinancialsService()
