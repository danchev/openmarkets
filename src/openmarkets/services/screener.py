"""Service layer for the yfinance screener API (added in yfinance 1.3.0).

Provides business logic for screening equities, ETFs and mutual funds
against predefined criteria. Acts as an intermediary between the MCP
tools layer and repository layer.
"""

from curl_cffi.requests import Session

from openmarkets.core.http import get_session
from openmarkets.repositories.screener import PredefinedScreen, YFinanceScreenerRepository
from openmarkets.schemas.screener import ScreenerResult
from openmarkets.services.utils import ToolRegistrationMixin, tool


class ScreenerService(ToolRegistrationMixin):
    """
    Service layer for screener-related business logic.

    Unlike every other tool in this project, which takes a known
    ticker/sector/industry, search_screener_matches() discovers instruments
    matching criteria rather than looking up something already identified.
    """

    def __init__(self, repository: YFinanceScreenerRepository | None = None, session: Session | None = None):
        """Initialize the ScreenerService.

        Args:
            repository: Repository instance for data access. Defaults to YFinanceScreenerRepository.
            session: HTTP session for requests. Defaults to the shared process-wide session.
        """
        self.repository = repository or YFinanceScreenerRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests.

        Falls back to the process-wide shared session so that no session is
        created at import time.
        """
        return self._session if self._session is not None else get_session()

    @tool
    def search_screener_matches(self, query: PredefinedScreen, count: int = 25, offset: int = 0) -> ScreenerResult:
        """
        Run a predefined screener query to discover matching equities, ETFs or
        mutual funds - for example the current day's top gainers, the most
        actively traded stocks, or top-performing ETFs.

        Args:
            query (str): Name of a predefined screen. One of: aggressive_small_caps,
                bond_etfs, conservative_foreign_funds, day_gainers, day_losers,
                growth_technology_stocks, high_yield_bond, most_actives,
                most_shorted_stocks, portfolio_anchors, small_cap_gainers,
                solid_large_growth_funds, solid_midcap_growth_funds, technology_etfs,
                top_etfs_us, top_mutual_funds, top_performing_etfs,
                undervalued_growth_stocks, undervalued_large_caps.
            count (int, optional): Maximum number of results to return. Defaults to 25.
                Must be positive; Yahoo caps this at 250.
            offset (int, optional): Number of results to skip, for pagination. Defaults to 0.
                Must be non-negative.

        Returns:
            ScreenerResult: Matching instruments and the total match count.

        Raises:
            ValueError: If query is unknown, or count/offset is out of range.
        """
        return self.repository.screen(query, count=count, offset=offset, session=self.session)


screener_service = ScreenerService()
