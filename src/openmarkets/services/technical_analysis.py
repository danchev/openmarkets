from typing import Annotated

from curl_cffi.requests import Session

from openmarkets.repositories.technical_analysis import (
    ITechnicalAnalysisRepository,
    YFinanceTechnicalAnalysisRepository,
)
from openmarkets.schemas.technical_analysis import (
    SupportResistanceLevelsDict,
    TechnicalIndicatorsDict,
    VolatilityMetricsDict,
)
from openmarkets.services.utils import ToolRegistrationMixin


class TechnicalAnalysisService(ToolRegistrationMixin):
    """
    Service layer for technical analysis business logic.
    Provides methods to retrieve technical indicators, volatility metrics, and support/resistance levels for a given ticker.
    """

    def __init__(self, repository: ITechnicalAnalysisRepository | None = None, session: Session | None = None):
        """
        Initialize the TechnicalAnalysisService with a repository dependency.

        Args:
            repository (ITechnicalAnalysisRepository): The repository instance for data access.
        """
        self.repository = repository or YFinanceTechnicalAnalysisRepository()
        self.session = session or Session(impersonate="chrome")

    def get_technical_indicators(
        self, ticker: Annotated[str, "The symbol of the security."], period: str = "6mo"
    ) -> TechnicalIndicatorsDict:
        """
        Retrieve technical indicators for a given ticker and period.

        Args:
            ticker (str): The symbol of the security.
            period (str, optional): Time period for indicators (e.g., '6mo'). Defaults to '6mo'.

        Returns:
            TechnicalIndicatorsDict: Technical indicators data.
        """
        return self.repository.get_technical_indicators(ticker, period, session=self.session)

    def get_volatility_metrics(
        self, ticker: Annotated[str, "The symbol of the security."], period: str = "1y"
    ) -> VolatilityMetricsDict:
        """
        Retrieve volatility metrics for a given ticker and period.

        Args:
            ticker (str): The symbol of the security.
            period (str, optional): Time period for metrics (e.g., '1y'). Defaults to '1y'.

        Returns:
            VolatilityMetricsDict: Volatility metrics data.
        """
        return self.repository.get_volatility_metrics(ticker, period, session=self.session)

    def get_support_resistance_levels(
        self, ticker: Annotated[str, "The symbol of the security."], period: str = "6mo"
    ) -> SupportResistanceLevelsDict:
        """
        Retrieve support and resistance levels for a given ticker and period.

        Args:
            ticker (str): The symbol of the security.
            period (str, optional): Time period for levels (e.g., '6mo'). Defaults to '6mo'.

        Returns:
            SupportResistanceLevelsDict: Support and resistance levels data.
        """
        return self.repository.get_support_resistance_levels(ticker, period, session=self.session)


technical_analysis_service = TechnicalAnalysisService()
