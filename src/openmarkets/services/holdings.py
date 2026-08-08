"""Service layer for holdings data operations.

Provides business logic for retrieving major holders, institutional holdings,
mutual fund holdings, insider transactions, and comprehensive holdings reports.
Acts as an intermediary between the MCP tools layer and repository layer.
"""

from typing import Annotated

from curl_cffi.requests import Session

from openmarkets.core.http import get_session
from openmarkets.repositories.holdings import IHoldingsRepository, YFinanceHoldingsRepository
from openmarkets.schemas.holdings import (
    FullHoldings,
    InsiderPurchase,
    StockInstitutionalHoldings,
    StockMajorHolders,
    StockMutualFundHoldings,
)
from openmarkets.services.utils import ToolRegistrationMixin, tool


class HoldingsService(ToolRegistrationMixin):
    """
    Service layer for holdings-related business logic.
    Provides methods to retrieve major holders, institutional holdings, mutual fund holdings, insider purchases, and full holdings data for a given ticker.
    """

    def __init__(self, repository: IHoldingsRepository | None = None, session: Session | None = None):
        """Initialize the HoldingsService.

        Args:
            repository: Repository instance for data access. Defaults to YFinanceHoldingsRepository.
            session: HTTP session for requests. Defaults to chrome-impersonating Session.
        """
        self.repository = repository or YFinanceHoldingsRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests.

        Falls back to the process-wide shared session so that no session is
        created at import time.
        """
        return self._session if self._session is not None else get_session()

    @tool
    def get_major_holders(self, ticker: Annotated[str, "The symbol of the security."]) -> list[StockMajorHolders]:
        """
        Retrieve major holders for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Major holders data from the repository.
        """
        return self.repository.get_major_holders(ticker, session=self.session)

    @tool
    def get_institutional_holdings(
        self, ticker: Annotated[str, "The symbol of the security."]
    ) -> list[StockInstitutionalHoldings]:
        """
        Retrieve institutional holdings for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Institutional holdings data from the repository.
        """
        return self.repository.get_institutional_holdings(ticker, session=self.session)

    @tool
    def get_mutual_fund_holdings(
        self, ticker: Annotated[str, "The symbol of the security."]
    ) -> list[StockMutualFundHoldings]:
        """
        Retrieve mutual fund holdings for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Mutual fund holdings data from the repository.
        """
        return self.repository.get_mutual_fund_holdings(ticker, session=self.session)

    @tool
    def get_insider_purchases(self, ticker: Annotated[str, "The symbol of the security."]) -> list[InsiderPurchase]:
        """
        Retrieve insider purchases for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Insider purchases data from the repository.
        """
        return self.repository.get_insider_purchases(ticker, session=self.session)

    @tool
    def get_full_holdings(self, ticker: Annotated[str, "The symbol of the security."]) -> FullHoldings:
        """
        Retrieve a full set of holdings data for a given ticker, aggregating all available holdings information.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            FullHoldings: All holdings data for the ticker.
        """
        return FullHoldings(
            major_holders=self.repository.get_major_holders(ticker, session=self.session),
            institutional_holdings=self.repository.get_institutional_holdings(ticker, session=self.session),
            mutual_fund_holdings=self.repository.get_mutual_fund_holdings(ticker, session=self.session),
            insider_purchases=self.repository.get_insider_purchases(ticker, session=self.session),
        )


holdings_service = HoldingsService()
