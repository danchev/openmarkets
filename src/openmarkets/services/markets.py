"""Service layer for market data operations.

Provides business logic for retrieving market summaries, market status,
and overall market performance data. Acts as an intermediary between
the MCP tools layer and repository layer.
"""

from typing import Annotated

from curl_cffi.requests import Session

from openmarkets.core.cache import cached
from openmarkets.core.http import get_session
from openmarkets.repositories.markets import YFinanceMarketsRepository
from openmarkets.schemas.markets import MarketStatus, MarketSummary, MarketType
from openmarkets.services.utils import ToolRegistrationMixin, tool


class MarketsService(ToolRegistrationMixin):
    """
    Service layer for market-related business logic.
    Provides methods to retrieve market summaries, indices data, and sector performance.
    """

    def __init__(self, repository: YFinanceMarketsRepository | None = None, session: Session | None = None):
        """Initialize the MarketsService.

        Args:
            repository: Repository instance for data access. Defaults to YFinanceMarketsRepository.
            session: HTTP session for requests. Defaults to chrome-impersonating Session.
        """
        self.repository = repository or YFinanceMarketsRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests.

        Falls back to the process-wide shared session so that no session is
        created at import time.
        """
        return self._session if self._session is not None else get_session()

    @tool
    @cached(ttl=300.0)
    def get_market_summary(self, market: Annotated[str, MarketType.__members__]) -> MarketSummary:
        """
        Retrieve a summary of the overall market performance.

        Returns:
            dict: Market summary data.
        """
        return self.repository.get_market_summary(market=market, session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_market_status(self, market: Annotated[str, MarketType.__members__]) -> MarketStatus:
        """
        Retrieve the current status of major market indices.

        Returns:
            dict: Market indices status data.
        """
        return self.repository.get_market_status(market=market, session=self.session)


markets_service = MarketsService()
