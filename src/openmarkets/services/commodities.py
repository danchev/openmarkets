"""Service layer for commodities and futures market data operations."""

from typing import Annotated

from curl_cffi.requests import Session

from openmarkets.core.cache import cached
from openmarkets.core.http import get_session
from openmarkets.repositories.commodities import CommoditiesRepository, WSJCommoditiesRepository
from openmarkets.schemas.commodities import (
    CommodityHistory,
    CommodityQuote,
    FertilizerIndexSeries,
)
from openmarkets.services.utils import ToolRegistrationMixin, tool


class CommoditiesService(ToolRegistrationMixin):
    """Service layer for physical commodities and futures.

    Provides methods to retrieve real-time quotes and historical price charts
    for Energy (WTI, Brent, Gas), Metals (Gold, Silver, Copper), and Agriculture (Wheat, Corn).
    """

    def __init__(
        self,
        repository: CommoditiesRepository | None = None,
        session: Session | None = None,
    ) -> None:
        """Initialize the CommoditiesService.

        Args:
            repository: Repository instance for data access. Defaults to WSJCommoditiesRepository.
            session: HTTP session for requests.
        """
        self.repository: CommoditiesRepository = repository or WSJCommoditiesRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests."""
        return self._session if self._session is not None else get_session()

    @tool
    @cached(ttl=300.0)
    def get_commodity_quote(
        self,
        symbol: Annotated[
            str,
            "Commodity symbol or alias (e.g. 'CRUDE_OIL', 'BRENT_CRUDE', 'NATURAL_GAS', 'GOLD', 'SILVER', 'COPPER', 'WHEAT', 'CORN', 'SOYBEANS')",
        ],
    ) -> CommodityQuote:
        """Retrieve the latest price quote for a physical commodity or futures contract."""
        return self.repository.get_commodity_quote(symbol=symbol, session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_commodity_history(
        self,
        symbol: Annotated[
            str,
            "Commodity symbol (e.g. 'CRUDE_OIL', 'GOLD', 'WHEAT')",
        ],
        timeframe: Annotated[str, "Time span duration: 'D7' (7 days), 'M1' (1 month), 'P1Y' (1 year), 'all'"] = "P1Y",
        step: Annotated[str, "Bar frequency: 'P1D' (daily), 'PT1M' (1-minute intraday)"] = "P1D",
    ) -> CommodityHistory:
        """Retrieve historical price timeseries for a physical commodity or future."""
        return self.repository.get_commodity_history(
            symbol=symbol,
            timeframe=timeframe,
            step=step,
            session=self.session,
        )

    @tool
    @cached(ttl=300.0)
    def get_energy_prices(self) -> list[CommodityQuote]:
        """Retrieve current prices for benchmark energy commodities (WTI Crude, Brent, Natural Gas, Gasoline, Heating Oil)."""
        return self.repository.get_energy_quotes(session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_metals_prices(self) -> list[CommodityQuote]:
        """Retrieve current prices for precious and industrial metals (Gold, Silver, Copper, Platinum, Palladium)."""
        return self.repository.get_metals_quotes(session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_agriculture_prices(self) -> list[CommodityQuote]:
        """Retrieve current prices for major agricultural grains (Wheat, Corn, Soybeans, Coffee, Sugar)."""
        return self.repository.get_agriculture_quotes(session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_livestock_prices(self) -> list[CommodityQuote]:
        """Retrieve current snapshot prices for livestock commodities (Live Cattle, Feeder Cattle, Lean Hogs)."""
        return self.repository.get_livestock_quotes(session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_softs_prices(self) -> list[CommodityQuote]:
        """Retrieve current snapshot prices for soft commodities (Coffee, Sugar, Cocoa, Cotton)."""
        return self.repository.get_softs_quotes(session=self.session)

    @tool
    @cached(ttl=600.0)
    def get_fertilizer_price_index(self) -> FertilizerIndexSeries:
        """Retrieve Green Markets North American Fertilizer Price Index timeseries.

        Benchmark weekly index published by Green Markets / Bloomberg / Dow Jones tracking raw agricultural input costs.

        Returns:
            FertilizerIndexSeries with latest price index and historical observations.
        """
        return self.repository.get_fertilizer_index(session=self.session)


commodities_service = CommoditiesService()
