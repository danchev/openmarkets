"""Service layer for market data operations.

Provides business logic for retrieving market summaries, market status,
and overall market performance data. Acts as an intermediary between
the MCP tools layer and repository layer.
"""

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
        """Initialize the MarketsService.

        Args:
            repository: Repository instance for data access. Defaults to YFinanceMarketsRepository.
            session: HTTP session for requests. Defaults to chrome-impersonating Session.
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
