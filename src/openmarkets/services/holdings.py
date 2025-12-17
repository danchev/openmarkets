from typing import Annotated

from curl_cffi.requests import Session

from openmarkets.repositories.holdings import IHoldingsRepository, YFinanceHoldingsRepository
from openmarkets.services.utils import ToolRegistrationMixin


class HoldingsService(ToolRegistrationMixin):
    """
    Service layer for holdings-related business logic.
    Provides methods to retrieve major holders, institutional holdings, mutual fund holdings, insider purchases, and full holdings data for a given ticker.
    """

    def __init__(self, repository: IHoldingsRepository | None = None, session: None = None):
        """
        Initialize the HoldingsService with a repository dependency.

        Args:
            repository (IHoldingsRepository): The repository instance for data access.
        """
        self.repository = repository or YFinanceHoldingsRepository()
        self.session = session or Session(impersonate="chrome")

    def get_major_holders(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve major holders for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Major holders data from the repository.
        """
        return self.repository.get_major_holders(ticker, session=self.session)

    def get_institutional_holdings(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve institutional holdings for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Institutional holdings data from the repository.
        """
        return self.repository.get_institutional_holdings(ticker, session=self.session)

    def get_mutual_fund_holdings(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve mutual fund holdings for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Mutual fund holdings data from the repository.
        """
        return self.repository.get_mutual_fund_holdings(ticker, session=self.session)

    def get_insider_purchases(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve insider purchases for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Insider purchases data from the repository.
        """
        return self.repository.get_insider_purchases(ticker, session=self.session)

    def get_full_holdings(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve a full set of holdings data for a given ticker, aggregating all available holdings information.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            dict: Dictionary containing all holdings data for the ticker.
        """
        return {
            "major_holders": self.repository.get_major_holders(ticker, session=self.session),
            "institutional_holdings": self.repository.get_institutional_holdings(ticker, session=self.session),
            "mutual_fund_holdings": self.repository.get_mutual_fund_holdings(ticker, session=self.session),
            "insider_purchases": self.repository.get_insider_purchases(ticker, session=self.session),
            "insider_roster_holders": self.repository.get_insider_roster_holders(ticker, session=self.session),
        }


holdings_service = HoldingsService()
