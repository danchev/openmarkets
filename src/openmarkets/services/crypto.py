"""Service layer for cryptocurrency operations.

Provides business logic for retrieving cryptocurrency information, historical data,
top cryptocurrencies by market cap, and sentiment indicators. Acts as an intermediary
between the MCP tools layer and repository layer.
"""

from typing import Annotated

from curl_cffi.requests import Session
from pydantic import Field

from openmarkets.core.http import get_session
from openmarkets.core.types import Interval, Period, Ticker
from openmarkets.repositories.crypto import YFinanceCryptoRepository
from openmarkets.schemas.crypto import CryptoFastInfo, CryptoHistory, CryptoSentiment
from openmarkets.services.utils import ToolRegistrationMixin, tool


class CryptoService(ToolRegistrationMixin):
    """
    Service layer for cryptocurrency-related operations.
    Provides methods to fetch crypto info, history, top cryptocurrencies, and fear/greed proxy data.
    """

    def __init__(self, repository: YFinanceCryptoRepository | None = None, session: Session | None = None):
        """Initialize the CryptoService.

        Args:
            repository: Repository instance for data access. Defaults to YFinanceCryptoRepository.
            session: HTTP session for requests. Defaults to chrome-impersonating Session.
        """
        self.repository = repository or YFinanceCryptoRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests.

        Falls back to the process-wide shared session so that no session is
        created at import time.
        """
        return self._session if self._session is not None else get_session()

    @tool
    def get_crypto_info(self, ticker: Ticker) -> CryptoFastInfo:
        """
        Retrieve fast information for a specific cryptocurrency.

        Args:
            ticker (str): The symbol of the cryptocurrency (e.g., 'BTC').

        Returns:
            CryptoFastInfo: Fast info data for the given ticker.
        """
        return self.repository.get_crypto_info(ticker, session=self.session)

    @tool
    def get_crypto_history(
        self, ticker: Ticker, period: Period = "1y", interval: Interval = "1d"
    ) -> list[CryptoHistory]:
        """
        Retrieve historical price data for a cryptocurrency.

        Args:
            ticker (str): The symbol of the cryptocurrency.
            period (str, optional): Time period for history. Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max. Defaults to '1y'.
            interval (str, optional): Data interval. Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo. Defaults to '1d'.

        Returns:
            list[CryptoHistory]: List of historical data points.
        """
        return self.repository.get_crypto_history(ticker, period, interval, session=self.session)

    @tool
    def get_top_cryptocurrencies(self, count: Annotated[int, Field(ge=1, le=20)] = 10) -> list[CryptoFastInfo]:
        """
        Retrieve quotes for the configured major-cryptocurrency watchlist.

        Args:
            count (int, optional): Number of top cryptocurrencies to fetch. Defaults to 10.

        Returns:
            list[CryptoFastInfo]: List of top cryptocurrencies.
        """
        return self.repository.get_top_cryptocurrencies(count)

    @tool
    def get_crypto_fear_greed_proxy(self, tickers: list[str] | None = None) -> CryptoSentiment:
        """
        Retrieve a proxy value for the crypto fear and greed index.

        Args:
            tickers (list[str] | None, optional): List of crypto tickers to include. If None, uses a default set.

        Returns:
            CryptoSentiment: Sentiment proxy and supporting per-asset data.
        """
        return self.repository.get_crypto_fear_greed_proxy(tickers, session=self.session)


crypto_service = CryptoService()
