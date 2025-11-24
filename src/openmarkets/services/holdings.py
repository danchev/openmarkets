from typing import Annotated

from openmarkets.repositories.holdings import IHoldingsRepository, YFinanceHoldingsRepository
from openmarkets.services.utils import ToolRegistrationMixin


class HoldingsService(ToolRegistrationMixin):
    """
    Service layer for holdings-related business logic.
    Provides methods to retrieve major holders, institutional holdings, mutual fund holdings, insider purchases, and full holdings data for a given ticker.
    """

    def __init__(self, repository: IHoldingsRepository | None = None):
        """
        Initialize the HoldingsService with a repository dependency.

        Args:
            repository (IHoldingsRepository): The repository instance for data access.
        """
        self.repository = repository or YFinanceHoldingsRepository()

    def get_major_holders(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve major holders for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Major holders data from the repository.
        """
        return self.repository.fetch_major_holders(ticker)

    def get_institutional_holdings(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve institutional holdings for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Institutional holdings data from the repository.
        """
        return self.repository.fetch_institutional_holdings(ticker)

    def get_mutual_fund_holdings(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve mutual fund holdings for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Mutual fund holdings data from the repository.
        """
        return self.repository.fetch_mutual_fund_holdings(ticker)

    def get_insider_purchases(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve insider purchases for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Insider purchases data from the repository.
        """
        return self.repository.fetch_insider_purchases(ticker)

    def get_full_holdings(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve a full set of holdings data for a given ticker, aggregating all available holdings information.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            dict: Dictionary containing all holdings data for the ticker.
        """
        return {
            "major_holders": self.repository.fetch_major_holders(ticker),
            "institutional_holdings": self.repository.fetch_institutional_holdings(ticker),
            "mutual_fund_holdings": self.repository.fetch_mutual_fund_holdings(ticker),
            "insider_purchases": self.repository.fetch_insider_purchases(ticker),
            "insider_roster_holders": self.repository.fetch_insider_roster_holders(ticker),
        }


holdings_service = HoldingsService()
