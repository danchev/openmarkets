"""Service layer for stock analysis operations.

Provides business logic layer for retrieving analyst recommendations,
earnings estimates, revenue estimates, growth projections, and price targets.
Acts as an intermediary between the MCP tools layer and repository layer.
"""

from curl_cffi.requests import Session

from openmarkets.core.cache import cached
from openmarkets.core.concurrency import gather
from openmarkets.core.http import get_session
from openmarkets.core.types import Ticker
from openmarkets.repositories.analysis import YFinanceAnalysisRepository
from openmarkets.schemas.analysis import (
    AnalystPriceTargets,
    AnalystRecommendation,
    AnalystRecommendationChange,
    EarningsEstimate,
    EPSTrend,
    FullAnalysis,
    GrowthEstimates,
    RevenueEstimate,
)
from openmarkets.services.utils import ToolRegistrationMixin, tool


class AnalysisService(ToolRegistrationMixin):
    """
    Application service for analysis use cases.
    Provides methods to retrieve analyst recommendations, estimates, trends, and price targets for a given ticker.
    """

    def __init__(self, repository: YFinanceAnalysisRepository | None = None, session: Session | None = None):
        """Initialize the AnalysisService.

        Args:
            repository: Repository instance for data access. Defaults to YFinanceAnalysisRepository.
            session: HTTP session for requests. Defaults to chrome-impersonating Session.
        """
        self.repository = repository or YFinanceAnalysisRepository()
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
    def get_analyst_recommendations(self, ticker: Ticker) -> list[AnalystRecommendation]:
        """
        Retrieve analyst recommendations for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Analyst recommendations data from the repository.
        """
        return self.repository.get_analyst_recommendations(ticker, session=self.session)

    @tool
    def get_recommendation_changes(self, ticker: Ticker) -> list[AnalystRecommendationChange]:
        """
        Retrieve changes in analyst recommendations for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Recommendation changes data from the repository.
        """
        return self.repository.get_recommendation_changes(ticker, session=self.session)

    @tool
    def get_revenue_estimates(self, ticker: Ticker) -> list[RevenueEstimate]:
        """
        Retrieve revenue estimates for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Revenue estimates data from the repository.
        """
        return self.repository.get_revenue_estimates(ticker, session=self.session)

    @tool
    def get_earnings_estimates(self, ticker: Ticker) -> list[EarningsEstimate]:
        """
        Retrieve earnings estimates for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Earnings estimates data from the repository.
        """
        return self.repository.get_earnings_estimates(ticker, session=self.session)

    @tool
    def get_growth_estimates(self, ticker: Ticker) -> list[GrowthEstimates]:
        """
        Retrieve growth estimates for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Growth estimates data from the repository.
        """
        return self.repository.get_growth_estimates(ticker, session=self.session)

    @tool
    def get_eps_trends(self, ticker: Ticker) -> list[EPSTrend]:
        """
        Retrieve EPS (Earnings Per Share) trends for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: EPS trends data from the repository.
        """
        return self.repository.get_eps_trends(ticker, session=self.session)

    @tool
    def get_price_targets(self, ticker: Ticker) -> AnalystPriceTargets:
        """
        Retrieve price targets for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Price targets data from the repository.
        """
        return self.repository.get_price_targets(ticker, session=self.session)

    @tool
    def get_full_analysis(self, ticker: Ticker) -> FullAnalysis:
        """
        Retrieve a full analysis report for a given ticker, aggregating all available analysis data.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            FullAnalysis: All analysis data for the ticker.
        """
        session = self.session
        return FullAnalysis(
            **gather(
                {
                    "recommendations": lambda: self.repository.get_analyst_recommendations(ticker, session=session),
                    "recommendation_changes": lambda: self.repository.get_recommendation_changes(
                        ticker, session=session
                    ),
                    "revenue_estimates": lambda: self.repository.get_revenue_estimates(ticker, session=session),
                    "earnings_estimates": lambda: self.repository.get_earnings_estimates(ticker, session=session),
                    "growth_estimates": lambda: self.repository.get_growth_estimates(ticker, session=session),
                    "eps_trends": lambda: self.repository.get_eps_trends(ticker, session=session),
                    "price_targets": lambda: self.repository.get_price_targets(ticker, session=session),
                }
            )
        )


analysis_service = AnalysisService()
