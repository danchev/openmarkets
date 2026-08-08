"""Service layer for options data operations.

Provides business logic for retrieving option chains, expiration dates,
call/put options, volume analysis, moneyness filtering, and options skew.
Acts as an intermediary between the MCP tools layer and repository layer.
"""

from datetime import date

from curl_cffi import Session

from openmarkets.core.http import get_session
from openmarkets.core.types import Ticker
from openmarkets.repositories.options import OptionsRepository, YFinanceOptionsRepository
from openmarkets.schemas.options import (
    CallOption,
    OptionContractChain,
    OptionExpirationDate,
    OptionsByMoneyness,
    OptionsSkew,
    OptionsVolumeAnalysis,
    PutOption,
)
from openmarkets.services.utils import ToolRegistrationMixin, tool


class OptionsService(ToolRegistrationMixin):
    """
    Service layer for options-related business logic.
    Provides methods to retrieve option expiration dates, option chains, call/put options, volume analysis, and advanced analytics for a given ticker.
    """

    def __init__(self, repository: OptionsRepository | None = None, session: Session | None = None):
        """Initialize the OptionsService.

        Args:
            repository: Repository instance for data access. Defaults to YFinanceOptionsRepository.
            session: HTTP session for requests. Defaults to chrome-impersonating Session.
        """
        self.repository = repository or YFinanceOptionsRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests.

        Falls back to the process-wide shared session so that no session is
        created at import time.
        """
        return self._session if self._session is not None else get_session()

    @tool
    def get_option_expiration_dates(self, ticker: Ticker) -> list[OptionExpirationDate]:
        """
        Retrieve available option expiration dates for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[OptionExpirationDate]: List of available expiration dates.
        """
        return self.repository.get_option_expiration_dates(ticker, session=self.session)

    @tool
    def get_option_chain(self, ticker: Ticker, expiration: date | None = None) -> OptionContractChain:
        """
        Retrieve the option contract chain for a given ticker and expiration date.

        Args:
            ticker (str): The symbol of the security.
            expiration (date | None, optional): The expiration date. If None, uses the nearest expiration.

        Returns:
            OptionContractChain: The option contract chain data.
        """
        return self.repository.get_option_chain(ticker, expiration, session=self.session)

    @tool
    def get_call_options(self, ticker: Ticker, expiration: date | None = None) -> list[CallOption] | None:
        """
        Retrieve call options for a given ticker and expiration date.

        Args:
            ticker (str): The symbol of the security.
            expiration (date | None, optional): The expiration date. If None, uses the nearest expiration.

        Returns:
            list[CallOption] | None: List of call options or None if unavailable.
        """
        return self.repository.get_call_options(ticker, expiration, session=self.session)

    @tool
    def get_put_options(self, ticker: Ticker, expiration: date | None = None) -> list[PutOption] | None:
        """
        Retrieve put options for a given ticker and expiration date.

        Args:
            ticker (str): The symbol of the security.
            expiration (date | None, optional): The expiration date. If None, uses the nearest expiration.

        Returns:
            list[PutOption] | None: List of put options or None if unavailable.
        """
        return self.repository.get_put_options(ticker, expiration, session=self.session)

    @tool
    def get_options_volume_analysis(self, ticker: Ticker, expiration_date: str | None = None) -> OptionsVolumeAnalysis:
        """
        Retrieve options volume analysis for a given ticker and expiration date.

        Args:
            ticker (str): The symbol of the security.
            expiration_date (str | None, optional): The expiration date as a string. If None, uses the nearest expiration.

        Returns:
            dict: Volume analysis data.
        """
        return self.repository.get_options_volume_analysis(ticker, expiration_date, session=self.session)

    @tool
    def get_options_by_moneyness(
        self,
        ticker: Ticker,
        expiration_date: str | None = None,
        moneyness_range: float = 0.1,
    ) -> OptionsByMoneyness:
        """
        Retrieve options filtered by moneyness for a given ticker and expiration date.

        Args:
            ticker (str): The symbol of the security.
            expiration_date (str | None, optional): The expiration date as a string. If None, uses the nearest expiration.
            moneyness_range (float, optional): The moneyness range for filtering. Defaults to 0.1.

        Returns:
            dict: Options data filtered by moneyness.
        """
        return self.repository.get_options_by_moneyness(ticker, expiration_date, moneyness_range, session=self.session)

    @tool
    def get_options_skew(self, ticker: Ticker, expiration_date: str | None = None) -> OptionsSkew:
        """
        Retrieve options skew analysis for a given ticker and expiration date.

        Args:
            ticker (str): The symbol of the security.
            expiration_date (str | None, optional): The expiration date as a string. If None, uses the nearest expiration.

        Returns:
            dict: Options skew analysis data.
        """
        return self.repository.get_options_skew(ticker, expiration_date, session=self.session)


options_service = OptionsService()
