"""Service layer for macroeconomic telemetry and Federal Reserve Economic Data (FRED)."""

from curl_cffi.requests import Session

from openmarkets.core.cache import cached
from openmarkets.core.http import get_session
from openmarkets.repositories.macroeconomics import FREDMacroeconomicsRepository, MacroeconomicsRepository
from openmarkets.schemas.macroeconomics import (
    EmploymentSummary,
    FinancialStressSummary,
    GDPSummary,
    InflationExpectationsSummary,
    InflationSummary,
    InterestRatesSummary,
    LiquiditySummary,
    MacroeconomicSeries,
    PCESummary,
)
from openmarkets.services.utils import ToolRegistrationMixin, tool


class MacroeconomicsService(ToolRegistrationMixin):
    """Service layer for macroeconomic indicators and monetary policy telemetry.

    Provides tools for querying US inflation (CPI, Core PCE), labor markets (Unemployment, Nonfarm Payrolls),
    interest rate benchmarks (EFFR, SOFR), GDP growth, M2 money supply, Fed balance sheet assets,
    TIPS breakeven inflation expectations, and financial stress indices.
    """

    def __init__(
        self,
        repository: MacroeconomicsRepository | None = None,
        session: Session | None = None,
    ) -> None:
        """Initialize the MacroeconomicsService.

        Args:
            repository: Data repository instance. Defaults to FREDMacroeconomicsRepository.
            session: Optional HTTP session for requests.
        """
        self.repository = repository or FREDMacroeconomicsRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests."""
        return self._session if self._session is not None else get_session()

    @tool
    @cached(ttl=600.0)
    def get_cpi_inflation(self, limit: int = 24) -> InflationSummary:
        """Retrieve US Consumer Price Index (CPI) and Core CPI with year-over-year inflation rates.

        Args:
            limit: Number of recent monthly observations to include (default 24).

        Returns:
            InflationSummary containing Headline CPI, Core CPI, and YoY percentage inflation.
        """
        return self.repository.get_cpi(limit=limit, session=self.session)

    @tool
    @cached(ttl=600.0)
    def get_pce_inflation(self, limit: int = 24) -> PCESummary:
        """Retrieve US Core Personal Consumption Expenditures (PCE) Price Index (Fed's primary inflation target).

        Args:
            limit: Number of recent monthly observations to include (default 24).

        Returns:
            PCESummary containing latest Core PCE level, YoY inflation rate, and Fed 2% target reference.
        """
        return self.repository.get_pce(limit=limit, session=self.session)

    @tool
    @cached(ttl=600.0)
    def get_employment_indicators(self, limit: int = 24) -> EmploymentSummary:
        """Retrieve US labor market telemetry including Civilian Unemployment Rate and Nonfarm Payrolls.

        Args:
            limit: Number of recent monthly observations to include (default 24).

        Returns:
            EmploymentSummary with unemployment rate %, total payrolls, and monthly net job creation.
        """
        return self.repository.get_employment(limit=limit, session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_interest_rates_telemetry(self, limit: int = 30) -> InterestRatesSummary:
        """Retrieve benchmark US money market and monetary policy interest rates (EFFR and SOFR).

        Args:
            limit: Number of recent daily observations to include (default 30).

        Returns:
            InterestRatesSummary with Effective Federal Funds Rate (EFFR) and SOFR rates.
        """
        return self.repository.get_interest_rates(limit=limit, session=self.session)

    @tool
    @cached(ttl=600.0)
    def get_gdp_growth(self, limit: int = 20) -> GDPSummary:
        """Retrieve US Real GDP and Nominal GDP output levels with quarter-over-quarter annualized growth rates.

        Args:
            limit: Number of recent quarterly observations to include (default 20).

        Returns:
            GDPSummary with Real GDP, Nominal GDP, and annualized real economic growth rate.
        """
        return self.repository.get_gdp(limit=limit, session=self.session)

    @tool
    @cached(ttl=600.0)
    def get_money_supply_and_fed_balance_sheet(self, limit: int = 24) -> LiquiditySummary:
        """Retrieve US M2 Money Supply and Federal Reserve Balance Sheet (Total Assets) liquidity telemetry.

        Args:
            limit: Number of recent observations to include (default 24).

        Returns:
            LiquiditySummary containing M2 Money Supply ($B), M2 YoY growth, and Fed Balance Sheet ($M).
        """
        return self.repository.get_liquidity(limit=limit, session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_inflation_expectations(self, limit: int = 30) -> InflationExpectationsSummary:
        """Retrieve 5-Year and 10-Year market-implied Breakeven Inflation Rates from TIPS.

        Args:
            limit: Number of recent daily observations to include (default 30).

        Returns:
            InflationExpectationsSummary with 5Y and 10Y breakeven inflation rates (%).
        """
        return self.repository.get_inflation_expectations(limit=limit, session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_financial_stress_and_credit_spreads(self, limit: int = 30) -> FinancialStressSummary:
        """Retrieve St. Louis Fed Financial Stress Index and ICE BofA US High Yield OAS credit spreads.

        Args:
            limit: Number of recent observations to include (default 30).

        Returns:
            FinancialStressSummary containing stress index level, market condition interpretation, and high-yield spreads.
        """
        return self.repository.get_financial_stress(limit=limit, session=self.session)

    @tool
    @cached(ttl=600.0)
    def get_macroeconomic_series(self, series_id: str, limit: int = 50) -> MacroeconomicSeries:
        """Query historical observations and metadata for any valid Federal Reserve Economic Data (FRED) series identifier.

        Examples: 'MORTGAGE30US' (30-Year Fixed Mortgage Rate), 'UMCSENT' (Consumer Sentiment), 'INDPRO' (Industrial Production).

        Args:
            series_id: Valid FRED series identifier (e.g. 'CPIAUCSL', 'MORTGAGE30US', 'INDPRO').
            limit: Number of recent observations to return (default 50, 0 for all available).

        Returns:
            MacroeconomicSeries with series title, units, frequency, latest release, and data points.
        """
        return self.repository.get_series(series_id=series_id, limit=limit, session=self.session)


macroeconomics_service = MacroeconomicsService()
