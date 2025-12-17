from typing import Annotated

from curl_cffi.requests import Session

from openmarkets.repositories.crypto import ICryptoRepository, YFinanceCryptoRepository
from openmarkets.schemas.crypto import CryptoFastInfo, CryptoHistory
from openmarkets.services.utils import ToolRegistrationMixin


class CryptoService(ToolRegistrationMixin):
    """
    Service layer for cryptocurrency-related operations.
    Provides methods to fetch crypto info, history, top cryptocurrencies, and fear/greed proxy data.
    """

    def __init__(self, repository: ICryptoRepository | None = None, session: None = None):
        """
        Initialize the CryptoService with a repository dependency.

        Args:
            repository (ICryptoRepository): The repository instance for data access.
        """
        self.repository = repository or YFinanceCryptoRepository()
        self.session = session or Session(impersonate="chrome")

    def get_crypto_info(self, ticker: Annotated[str, "The symbol of the security."]) -> CryptoFastInfo:
        """
        Retrieve fast information for a specific cryptocurrency.

        Args:
            ticker (str): The symbol of the cryptocurrency (e.g., 'BTC').

        Returns:
            CryptoFastInfo: Fast info data for the given ticker.
        """
        return self.repository.get_crypto_info(ticker, session=self.session)

    def get_crypto_history(
        self, ticker: Annotated[str, "The symbol of the security."], period: str = "1y", interval: str = "1d"
    ) -> list[CryptoHistory]:
        """
        Retrieve historical price data for a cryptocurrency.

        Args:
            ticker (str): The symbol of the cryptocurrency.
            period (str, optional): Time period for history (e.g., '1y', '6mo'). Defaults to '1y'.
            interval (str, optional): Data interval (e.g., '1d', '1h'). Defaults to '1d'.

        Returns:
            list[CryptoHistory]: List of historical data points.
        """
        return self.repository.get_crypto_history(ticker, period, interval, session=self.session)

    def get_top_cryptocurrencies(self, count: int = 10) -> list[CryptoFastInfo]:
        """
        Retrieve a list of the top cryptocurrencies by market cap or volume.

        Args:
            count (int, optional): Number of top cryptocurrencies to fetch. Defaults to 10.

        Returns:
            list[CryptoFastInfo]: List of top cryptocurrencies.
        """
        return self.repository.get_top_cryptocurrencies(count)

    def get_crypto_fear_greed_proxy(self, tickers: list[str] | None = None):
        """
        Retrieve a proxy value for the crypto fear and greed index.

        Args:
            tickers (list[str] | None, optional): List of crypto tickers to include. If None, uses a default set.

        Returns:
            str: Proxy value or description for the fear/greed index.
        """
        return self.repository.get_crypto_fear_greed_proxy(tickers, session=self.session)


crypto_service = CryptoService()
