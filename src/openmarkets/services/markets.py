"""Service layer for market data operations.

Provides business logic for retrieving market summaries, market status,
and overall market performance data. Acts as an intermediary between
the MCP tools layer and repository layer.
"""

from typing import Annotated

from curl_cffi.requests import Session

from openmarkets.core.cache import cached
from openmarkets.core.http import get_session
from openmarkets.repositories.markets import WSJMarketsRepository, YFinanceMarketsRepository
from openmarkets.schemas.markets import GlobalIndexQuote, GlobalMarketSnapshot, MarketStatus, MarketSummary, MarketType
from openmarkets.services.utils import ToolRegistrationMixin, tool


class MarketsService(ToolRegistrationMixin):
    """
    Service layer for market-related business logic.
    Provides methods to retrieve market summaries, indices data, and sector performance.
    """

    def __init__(
        self,
        repository: YFinanceMarketsRepository | None = None,
        wsj_repository: WSJMarketsRepository | None = None,
        session: Session | None = None,
    ):
        """Initialize the MarketsService.

        Args:
            repository: Repository instance for YFinance market data.
            wsj_repository: Repository instance for WSJ global indices and volatility data.
            session: HTTP session for requests. Defaults to chrome-impersonating Session.
        """
        self.repository = repository or YFinanceMarketsRepository()
        self.wsj_repository = wsj_repository or WSJMarketsRepository()
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

    @tool
    @cached(ttl=120.0)
    def get_global_indices(self) -> GlobalMarketSnapshot:
        """Retrieve real-time snapshot of major global equity benchmark indices.

        Includes US (S&P 500, Dow Jones, Nasdaq, Russell 2000), Europe (DAX 40, FTSE 100, CAC 40, Euro Stoxx 50),
        and Asia (Nikkei 225, Hang Seng) alongside CBOE VIX.

        Returns:
            GlobalMarketSnapshot with all international benchmark quotes.
        """
        return self.wsj_repository.get_global_indices(session=self.session)

    @tool
    @cached(ttl=60.0)
    def get_volatility_vix(self) -> GlobalIndexQuote:
        """Retrieve real-time quote for the CBOE Volatility Index (VIX / Wall Street Fear Gauge).

        Returns:
            GlobalIndexQuote with latest VIX index value and date.
        """
        return self.wsj_repository.get_volatility_vix(session=self.session)


markets_service = MarketsService()
