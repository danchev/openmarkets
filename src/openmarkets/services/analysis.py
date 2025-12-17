from typing import Annotated

from curl_cffi.requests import Session

from openmarkets.repositories.analysis import IAnalysisRepository, YFinanceAnalysisRepository
from openmarkets.services.utils import ToolRegistrationMixin


class AnalysisService(ToolRegistrationMixin):
    """
    Application service for analysis use cases.
    Provides methods to retrieve analyst recommendations, estimates, trends, and price targets for a given ticker.
    """

    def __init__(self, repository: IAnalysisRepository | None = None, session: None = None):
        """
        Initialize the AnalysisService with a repository dependency.

        Args:
            repository (IAnalysisRepository): The repository instance for data access.
        """
        self.repository = repository or YFinanceAnalysisRepository()
        self.session = session or Session(impersonate="chrome")

    def get_analyst_recommendations(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve analyst recommendations for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Analyst recommendations data from the repository.
        """
        return self.repository.get_analyst_recommendations(ticker, session=self.session)

    def get_recommendation_changes(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve changes in analyst recommendations for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Recommendation changes data from the repository.
        """
        return self.repository.get_recommendation_changes(ticker, session=self.session)

    def get_revenue_estimates(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve revenue estimates for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Revenue estimates data from the repository.
        """
        return self.repository.get_revenue_estimates(ticker, session=self.session)

    def get_earnings_estimates(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve earnings estimates for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Earnings estimates data from the repository.
        """
        return self.repository.get_earnings_estimates(ticker, session=self.session)

    def get_growth_estimates(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve growth estimates for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Growth estimates data from the repository.
        """
        return self.repository.get_growth_estimates(ticker, session=self.session)

    def get_eps_trends(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve EPS (Earnings Per Share) trends for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: EPS trends data from the repository.
        """
        return self.repository.get_eps_trends(ticker, session=self.session)

    def get_price_targets(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve price targets for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            Any: Price targets data from the repository.
        """
        return self.repository.get_price_targets(ticker, session=self.session)

    def get_full_analysis(self, ticker: Annotated[str, "The symbol of the security."]):
        """
        Retrieve a full analysis report for a given ticker, aggregating all available analysis data.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            dict: Dictionary containing all analysis data for the ticker.
        """
        return {
            "recommendations": self.repository.get_analyst_recommendations(ticker, session=self.session),
            "recommendation_changes": self.repository.get_recommendation_changes(ticker, session=self.session),
            "revenue_estimates": self.repository.get_revenue_estimates(ticker, session=self.session),
            "earnings_estimates": self.repository.get_earnings_estimates(ticker, session=self.session),
            "growth_estimates": self.repository.get_growth_estimates(ticker, session=self.session),
            "eps_trends": self.repository.get_eps_trends(ticker, session=self.session),
            "price_targets": self.repository.get_price_targets(ticker, session=self.session),
        }


analysis_service = AnalysisService()
