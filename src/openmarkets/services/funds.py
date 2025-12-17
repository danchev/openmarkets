from typing import Annotated

from curl_cffi.requests import Session

from openmarkets.repositories.funds import IFundsRepository, YFinanceFundsRepository
from openmarkets.schemas.funds import (
    FundAssetClassHolding,
    FundBondHolding,
    FundEquityHolding,
    FundInfo,
    FundOperations,
    FundOverview,
    FundSectorWeighting,
    FundTopHolding,
)
from openmarkets.services.utils import ToolRegistrationMixin


class FundsService(ToolRegistrationMixin):
    """
    Service layer for fund-related business logic.
    Provides methods to retrieve fund information, holdings, sector weightings, operations, and overviews for a given ticker.
    """

    def __init__(self, repository: IFundsRepository | None = None, session: None = None):
        """
        Initialize the FundsService with a repository dependency.

        Args:
            repository (IFundsRepository): The repository instance for data access.
        """
        self.repository = repository or YFinanceFundsRepository()
        self.session = session or Session(impersonate="chrome")

    def get_fund_info(self, ticker: Annotated[str, "The symbol of the security."]) -> FundInfo:
        """
        Retrieve general information for a specific fund.

        Args:
            ticker (str): The symbol of the fund.

        Returns:
            FundInfo: Information about the fund.
        """
        return self.repository.get_fund_info(ticker, session=self.session)

    def get_fund_sector_weighting(
        self, ticker: Annotated[str, "The symbol of the security."]
    ) -> FundSectorWeighting | None:
        """
        Retrieve sector weighting data for a specific fund.

        Args:
            ticker (str): The symbol of the fund.

        Returns:
            FundSectorWeighting | None: Sector weighting data or None if unavailable.
        """
        return self.repository.get_fund_sector_weighting(ticker, session=self.session)

    def get_fund_operations(self, ticker: Annotated[str, "The symbol of the security."]) -> FundOperations | None:
        """
        Retrieve operations data for a specific fund.

        Args:
            ticker (str): The symbol of the fund.

        Returns:
            FundOperations | None: Operations data or None if unavailable.
        """
        return self.repository.get_fund_operations(ticker, session=self.session)

    def get_fund_overview(self, ticker: Annotated[str, "The symbol of the security."]) -> FundOverview | None:
        """
        Retrieve an overview for a specific fund.

        Args:
            ticker (str): The symbol of the fund.

        Returns:
            FundOverview | None: Overview data or None if unavailable.
        """
        return self.repository.get_fund_overview(ticker, session=self.session)

    def get_fund_top_holdings(self, ticker: Annotated[str, "The symbol of the security."]) -> list[FundTopHolding]:
        """
        Retrieve the top holdings for a specific fund.

        Args:
            ticker (str): The symbol of the fund.

        Returns:
            list[FundTopHolding]: List of top holdings in the fund.
        """
        return self.repository.get_fund_top_holdings(ticker, session=self.session)

    def get_fund_bond_holdings(self, ticker: Annotated[str, "The symbol of the security."]) -> list[FundBondHolding]:
        """
        Retrieve the bond holdings for a specific fund.

        Args:
            ticker (str): The symbol of the fund.

        Returns:
            list[FundBondHolding]: List of bond holdings in the fund.
        """
        return self.repository.get_fund_bond_holdings(ticker, session=self.session)

    def get_fund_equity_holdings(
        self, ticker: Annotated[str, "The symbol of the security."]
    ) -> list[FundEquityHolding]:
        """
        Retrieve the equity holdings for a specific fund.

        Args:
            ticker (str): The symbol of the fund.

        Returns:
            list[FundEquityHolding]: List of equity holdings in the fund.
        """
        return self.repository.get_fund_equity_holdings(ticker, session=self.session)

    def get_fund_asset_class_holdings(
        self, ticker: Annotated[str, "The symbol of the security."]
    ) -> FundAssetClassHolding | None:
        """
        Retrieve asset class holdings for a specific fund.

        Args:
            ticker (str): The symbol of the fund.

        Returns:
            FundAssetClassHolding | None: Asset class holdings data or None if unavailable.
        """
        return self.repository.get_fund_asset_class_holdings(ticker, session=self.session)


funds_service = FundsService()
