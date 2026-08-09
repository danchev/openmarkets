"""Service layer for fixed income, bond yields, and yield curve analytics."""

from typing import Annotated

from curl_cffi.requests import Session

from openmarkets.core.cache import cached
from openmarkets.core.http import get_session
from openmarkets.repositories.fixed_income import FixedIncomeRepository, WSJFixedIncomeRepository
from openmarkets.schemas.fixed_income import (
    FixedIncomeHistory,
    GlobalSovereignYields,
    TreasuryYieldCurve,
)
from openmarkets.services.utils import ToolRegistrationMixin, tool


class FixedIncomeService(ToolRegistrationMixin):
    """Service layer for fixed income, sovereign debt, and yield curve analytics.

    Provides methods to retrieve the US Treasury yield curve snapshot,
    recession indicators (2Y/10Y spread and inversion status), global 10-year sovereign yields,
    and historical yield rates.
    """

    def __init__(
        self,
        repository: FixedIncomeRepository | None = None,
        session: Session | None = None,
    ) -> None:
        """Initialize the FixedIncomeService.

        Args:
            repository: Repository instance for data access. Defaults to WSJFixedIncomeRepository.
            session: HTTP session for requests.
        """
        self.repository: FixedIncomeRepository = repository or WSJFixedIncomeRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests."""
        return self._session if self._session is not None else get_session()

    @tool
    @cached(ttl=300.0)
    def get_treasury_yield_curve(self) -> TreasuryYieldCurve:
        """Retrieve the complete US Treasury yield curve snapshot across all benchmark maturities (1M to 30Y).

        Includes calculated 2Y/10Y and 3M/10Y basis point spreads and yield curve inversion status.
        """
        return self.repository.get_treasury_yield_curve(session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_global_sovereign_yields(self) -> GlobalSovereignYields:
        """Retrieve benchmark 10-year sovereign bond yields across major global economies.

        Compares benchmark 10-year government bond yields for the United States, Germany (Bund),
        United Kingdom (Gilt), and Japan (JGB), including calculated spreads against the US 10-Year Treasury.

        Returns:
            Snapshot of global 10-year sovereign benchmark yields and yield differentials.
        """
        return self.repository.get_global_sovereign_yields(session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_treasury_yield_history(
        self,
        maturity: Annotated[
            str,
            "Treasury or sovereign maturity label (e.g. '10Y', '2Y', '5Y', '30Y', '3M', 'US10Y', 'DE10Y', 'UK10Y', 'JP10Y')",
        ],
        timeframe: Annotated[str, "Time span duration: 'D7', '1mo', 'P1Y', '5y', 'all'"] = "P1Y",
        step: Annotated[str, "Bar frequency: 'P1D' (daily)"] = "P1D",
    ) -> FixedIncomeHistory:
        """Retrieve historical yield timeseries for a specific Treasury or sovereign benchmark maturity."""
        return self.repository.get_yield_history(
            maturity=maturity,
            timeframe=timeframe,
            step=step,
            session=self.session,
        )


fixed_income_service = FixedIncomeService()
