"""Service layer for technical analysis operations.

Provides business logic for retrieving technical indicators, volatility metrics,
support and resistance levels for stock analysis. Acts as an intermediary between
the MCP tools layer and repository layer.
"""

from typing import Annotated

from curl_cffi.requests import Session
from pydantic import Field

from openmarkets.core.cache import cached
from openmarkets.core.http import get_session
from openmarkets.core.types import Period, Ticker
from openmarkets.repositories.technical_analysis import (
    WSJTechnicalAnalysisRepository,
    YFinanceTechnicalAnalysisRepository,
)
from openmarkets.schemas.technical_analysis import (
    SupportResistanceLevelsDict,
    TechnicalIndicatorsDict,
    VolatilityMetricsDict,
    WSJIndicatorSeries,
    WSJMACDSeries,
)
from openmarkets.services.utils import ToolRegistrationMixin, tool

PositiveWindow = Annotated[int, Field(ge=1, le=1000)]
RSIWindow = Annotated[int, Field(ge=2, le=1000)]


class TechnicalAnalysisService(ToolRegistrationMixin):
    """
    Service layer for technical analysis business logic.
    Provides methods to retrieve technical indicators, volatility metrics, and support/resistance levels for a given ticker.
    """

    def __init__(
        self,
        repository: YFinanceTechnicalAnalysisRepository | None = None,
        wsj_repository: WSJTechnicalAnalysisRepository | None = None,
        session: Session | None = None,
    ):
        """Initialize the TechnicalAnalysisService.

        Args:
            repository: Repository instance for YFinance data access.
            wsj_repository: Repository instance for WSJ Michelangelo server-side indicators.
            session: HTTP session for requests.
        """
        self.repository = repository or YFinanceTechnicalAnalysisRepository()
        self.wsj_repository = wsj_repository or WSJTechnicalAnalysisRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests.

        Falls back to the process-wide shared session so that no session is
        created at import time.
        """
        return self._session if self._session is not None else get_session()

    @tool
    def get_technical_indicators(self, ticker: Ticker, period: Period = "1y") -> TechnicalIndicatorsDict:
        """
        Retrieve technical indicators for a given ticker and period.

        Args:
            ticker (str): The symbol of the security.
            period (str, optional): Time period for indicators (e.g., '6mo'). Defaults to '6mo'.

        Returns:
            TechnicalIndicatorsDict: Technical indicators data.
        """
        return self.repository.get_technical_indicators(ticker, period, session=self.session)

    @tool
    def get_volatility_metrics(self, ticker: Ticker, period: Period = "1y") -> VolatilityMetricsDict:
        """
        Retrieve volatility metrics for a given ticker and period.

        Args:
            ticker (str): The symbol of the security.
            period (str, optional): Time period for metrics (e.g., '1y'). Defaults to '1y'.

        Returns:
            VolatilityMetricsDict: Volatility metrics data.
        """
        return self.repository.get_volatility_metrics(ticker, period, session=self.session)

    @tool
    def get_support_resistance_levels(self, ticker: Ticker, period: Period = "6mo") -> SupportResistanceLevelsDict:
        """
        Retrieve support and resistance levels for a given ticker and period.

        Args:
            ticker (str): The symbol of the security.
            period (str, optional): Time period for levels (e.g., '6mo'). Defaults to '6mo'.

        Returns:
            SupportResistanceLevelsDict: Support and resistance levels data.
        """
        return self.repository.get_support_resistance_levels(ticker, period, session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_wsj_sma(
        self,
        ticker: Ticker,
        window: PositiveWindow = 50,
        timeframe: str = "P1Y",
        step: str = "P1D",
    ) -> WSJIndicatorSeries:
        """Retrieve server-side computed Simple Moving Average (SMA) from WSJ Michelangelo.

        Calculated directly on WSJ charting servers, providing ultra-low-latency moving averages.

        Args:
            ticker: Symbol (e.g. 'AAPL', 'TSLA', 'SPX').
            window: Moving average calculation window period (default 50).
            timeframe: Timespan duration (e.g. 'P1M', 'P3M', 'P1Y', '5y').
            step: Bar step frequency (e.g. 'P1D', 'PT1M').

        Returns:
            WSJIndicatorSeries with timestamped price and computed SMA values.
        """
        return self.wsj_repository.get_sma(
            ticker=ticker,
            window=window,
            timeframe=timeframe,
            step=step,
            session=self.session,
        )

    @tool
    @cached(ttl=300.0)
    def get_wsj_ema(
        self,
        ticker: Ticker,
        window: PositiveWindow = 20,
        timeframe: str = "P1Y",
        step: str = "P1D",
    ) -> WSJIndicatorSeries:
        """Retrieve server-side computed Exponential Moving Average (EMA) from WSJ Michelangelo.

        Args:
            ticker: Symbol (e.g. 'NVDA', 'MSFT').
            window: Moving average calculation window period (default 20).
            timeframe: Timespan duration (e.g. 'P1M', 'P3M', 'P1Y').
            step: Bar step frequency (e.g. 'P1D', 'PT1M').

        Returns:
            WSJIndicatorSeries with timestamped price and computed EMA values.
        """
        return self.wsj_repository.get_ema(
            ticker=ticker,
            window=window,
            timeframe=timeframe,
            step=step,
            session=self.session,
        )

    @tool
    @cached(ttl=300.0)
    def get_wsj_rsi(
        self,
        ticker: Ticker,
        window: RSIWindow = 14,
        timeframe: str = "P1Y",
        step: str = "P1D",
    ) -> WSJIndicatorSeries:
        """Retrieve server-side computed Relative Strength Index (RSI) momentum indicator from WSJ.

        Args:
            ticker: Symbol (e.g. 'TSLA', 'AAPL').
            window: RSI calculation period (default 14).
            timeframe: Timespan duration (e.g. 'P1M', 'P3M', 'P1Y').
            step: Bar step frequency (e.g. 'P1D', 'PT1M').

        Returns:
            WSJIndicatorSeries with timestamped price and RSI values (0-100).
        """
        return self.wsj_repository.get_rsi(
            ticker=ticker,
            window=window,
            timeframe=timeframe,
            step=step,
            session=self.session,
        )

    @tool
    @cached(ttl=300.0)
    def get_wsj_macd(
        self,
        ticker: Ticker,
        fast_window: PositiveWindow = 12,
        slow_window: PositiveWindow = 26,
        signal_window: PositiveWindow = 9,
        timeframe: str = "P1Y",
        step: str = "P1D",
    ) -> WSJMACDSeries:
        """Retrieve server-side computed Moving Average Convergence Divergence (MACD) from WSJ.

        Calculates MACD line, signal line, and MACD histogram natively on WSJ charting servers.

        Args:
            ticker: Symbol (e.g. 'TSLA', 'AAPL').
            fast_window: Fast EMA period (default 12).
            slow_window: Slow EMA period (default 26).
            signal_window: Signal line EMA period (default 9).
            timeframe: Timespan duration (e.g. 'P1M', 'P3M', 'P1Y').
            step: Bar step frequency (e.g. 'P1D', 'PT1M').

        Returns:
            WSJMACDSeries containing timestamped price, MACD line, signal line, and histogram.
        """
        return self.wsj_repository.get_macd(
            ticker=ticker,
            fast_window=fast_window,
            slow_window=slow_window,
            signal_window=signal_window,
            timeframe=timeframe,
            step=step,
            session=self.session,
        )


technical_analysis_service = TechnicalAnalysisService()
