from typing import Annotated

from curl_cffi.requests import Session

from openmarkets.repositories.markets import IMarketsRepository, YFinanceMarketsRepository
from openmarkets.schemas.markets import MarketStatus, MarketSummary, MarketType
from openmarkets.services.utils import ToolRegistrationMixin


class MarketsService(ToolRegistrationMixin):
    """
    Service layer for market-related business logic.
    Provides methods to retrieve market summaries, indices data, and sector performance.
    """

    def __init__(self, repository: IMarketsRepository | None = None, session: None = None):
        """
        Initialize the MarketsService with a repository dependency.

        Args:
            repository (IMarketsRepository): The repository instance for data access.
        """
        self.repository = repository or YFinanceMarketsRepository()
        self.session = session or Session(impersonate="chrome")

    def get_market_summary(self, market: Annotated[str, MarketType.__members__]) -> MarketSummary:
        """
        Retrieve a summary of the overall market performance.

        Returns:
            dict: Market summary data.
        """
        return self.repository.get_market_summary(market=market, session=self.session)

    def get_market_status(self, market: Annotated[str, MarketType.__members__]) -> MarketStatus:
        """
        Retrieve the current status of major market indices.

        Returns:
            dict: Market indices status data.
        """
        return self.repository.get_market_status(market=market, session=self.session)


markets_service = MarketsService()
