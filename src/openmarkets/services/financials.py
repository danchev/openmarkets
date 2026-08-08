"""Service layer for financial statements and data operations.

Provides business logic for retrieving balance sheets, income statements,
cash flow statements, financial calendars, SEC filings, and EPS history.
Acts as an intermediary between the MCP tools layer and repository layer.
"""

from typing import Annotated

from curl_cffi.requests import Session

from openmarkets.core.concurrency import gather
from openmarkets.core.http import get_session
from openmarkets.repositories.financials import IFinancialsRepository, YFinanceFinancialsRepository
from openmarkets.schemas.financials import (
    BalanceSheetEntry,
    EPSHistoryEntry,
    FinancialCalendar,
    FullFinancials,
    IncomeStatementEntry,
    SecFilingRecord,
    TTMCashFlowStatementEntry,
    TTMIncomeStatementEntry,
)
from openmarkets.services.utils import ToolRegistrationMixin, tool


class FinancialsService(ToolRegistrationMixin):
    """
    Service layer for financials business logic.
    Provides methods to retrieve various financial statements, calendars, filings, and EPS history for a given ticker.
    """

    def __init__(self, repository: IFinancialsRepository | None = None, session: Session | None = None):
        """Initialize the FinancialsService.

        Args:
            repository: Repository instance for data access. Defaults to YFinanceFinancialsRepository.
            session: HTTP session for requests. Defaults to chrome-impersonating Session.
        """
        self.repository = repository or YFinanceFinancialsRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests.

        Falls back to the process-wide shared session so that no session is
        created at import time.
        """
        return self._session if self._session is not None else get_session()

    @tool
    def get_balance_sheet(self, ticker: Annotated[str, "The symbol of the security."]) -> list[BalanceSheetEntry]:
        """
        Retrieve the balance sheet for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[BalanceSheetEntry]: List of balance sheet entries.
        """
        return self.repository.get_balance_sheet(ticker, session=self.session)

    @tool
    def get_income_statement(self, ticker: Annotated[str, "The symbol of the security."]) -> list[IncomeStatementEntry]:
        """
        Retrieve the income statement for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[IncomeStatementEntry]: List of income statement entries.
        """
        return self.repository.get_income_statement(ticker, session=self.session)

    @tool
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

    @tool
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

    @tool
    def get_financial_calendar(self, ticker: Annotated[str, "The symbol of the security."]) -> FinancialCalendar:
        """
        Retrieve the financial calendar for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            FinancialCalendar: Financial calendar data.
        """
        return self.repository.get_financial_calendar(ticker, session=self.session)

    @tool
    def get_sec_filings(self, ticker: Annotated[str, "The symbol of the security."]) -> list[SecFilingRecord]:
        """
        Retrieve SEC filings for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[SecFilingRecord]: List of SEC filing records.
        """
        return self.repository.get_sec_filings(ticker, session=self.session)

    @tool
    def get_eps_history(self, ticker: Annotated[str, "The symbol of the security."]) -> list[EPSHistoryEntry]:
        """
        Retrieve EPS (Earnings Per Share) history for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[EPSHistoryEntry]: List of EPS history entries.
        """
        return self.repository.get_eps_history(ticker, session=self.session)

    @tool
    def get_full_financials(self, ticker: Annotated[str, "The symbol of the security."]) -> FullFinancials:
        """
        Retrieve a full set of financial data for a given ticker, aggregating all available financial statements and records.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            FullFinancials: All financial data for the ticker.
        """
        session = self.session
        return FullFinancials(
            **gather(
                {
                    "balance_sheet": lambda: self.repository.get_balance_sheet(ticker, session=session),
                    "income_statement": lambda: self.repository.get_income_statement(ticker, session=session),
                    "ttm_income_statement": lambda: self.repository.get_ttm_income_statement(ticker, session=session),
                    "ttm_cash_flow_statement": lambda: self.repository.get_ttm_cash_flow_statement(
                        ticker, session=session
                    ),
                    "financial_calendar": lambda: self.repository.get_financial_calendar(ticker, session=session),
                    "sec_filings": lambda: self.repository.get_sec_filings(ticker, session=session),
                    "eps_history": lambda: self.repository.get_eps_history(ticker, session=session),
                }
            )
        )


financials_service = FinancialsService()
