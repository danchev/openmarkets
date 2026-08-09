"""Service providing Foreign Exchange (Forex) tools."""

from curl_cffi.requests import Session

from openmarkets.core.cache import cached
from openmarkets.core.http import get_session
from openmarkets.repositories.forex import ForexRepository, WSJForexRepository
from openmarkets.schemas.forex import ForexHistory, ForexQuote
from openmarkets.services.utils import ToolRegistrationMixin, tool


class ForexService(ToolRegistrationMixin):
    """Service providing foreign exchange rates, currency pairs, and dollar index metrics."""

    def __init__(
        self,
        repository: ForexRepository | None = None,
        session: Session | None = None,
    ) -> None:
        self.repository = repository or WSJForexRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests."""
        return self._session if self._session is not None else get_session()

    @tool
    @cached(ttl=300.0)
    def get_forex_quote(self, pair: str) -> ForexQuote:
        """Fetch current or latest foreign exchange quote for a currency pair.

        Args:
            pair: Currency pair symbol (e.g. ``EURUSD``, ``USDJPY``, ``GBPUSD``, ``AUDUSD``, ``USDCAD``, ``USDCHF``).

        Returns:
            Real-time or latest exchange rate with timestamp and currency breakdown.
        """
        return self.repository.get_forex_quote(pair=pair, session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_forex_history(
        self,
        pair: str,
        timeframe: str = "P1Y",
        step: str = "P1D",
    ) -> ForexHistory:
        """Fetch historical timeseries exchange rate bars for a currency pair.

        Args:
            pair: Currency pair symbol (e.g. ``EURUSD``, ``USDJPY``).
            timeframe: Timespan duration (e.g. ``D7``, ``P1M``, ``P3M``, ``P1Y``, ``P5Y``, ``all``).
            step: Bar step frequency (e.g. ``P1D``, ``PT1M``).

        Returns:
            Historical OHLC exchange rate bars.
        """
        return self.repository.get_forex_history(
            pair=pair,
            timeframe=timeframe,
            step=step,
            session=self.session,
        )

    @tool
    @cached(ttl=300.0)
    def get_major_currencies(self) -> list[ForexQuote]:
        """Fetch real-time snapshot quotes for all major global currency pairs.

        Covers EUR/USD, USD/JPY, GBP/USD, AUD/USD, USD/CAD, USD/CHF, USD/CNY, USD/MXN, and USD/INR.

        Returns:
            List of major currency pair quotes.
        """
        return self.repository.get_major_currencies(session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_dollar_index_dxy(self) -> ForexQuote:
        """Fetch current US Dollar Index (DXY) quote.

        The US Dollar Index measures the value of the US dollar relative to a basket of major foreign currencies.

        Returns:
            Current DXY index quote.
        """
        return self.repository.get_dollar_index_dxy(session=self.session)


forex_service = ForexService()
