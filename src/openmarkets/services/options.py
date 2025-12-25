from datetime import date
from typing import Annotated

from curl_cffi import Session

from openmarkets.repositories.options import IOptionsRepository, YFinanceOptionsRepository
from openmarkets.schemas.options import (
    CallOption,
    OptionContractChain,
    OptionExpirationDate,
    PutOption,
)
from openmarkets.services.utils import ToolRegistrationMixin


class OptionsService(ToolRegistrationMixin):
    """
    Service layer for options-related business logic.
    Provides methods to retrieve option expiration dates, option chains, call/put options, volume analysis, and advanced analytics for a given ticker.
    """

    def __init__(self, repository: IOptionsRepository | None = None, session: Session | None = None):
        """
        Initialize the OptionsService with a repository dependency.

        Args:
            repository (IOptionsRepository): The repository instance for data access.
        """
        self.repository = repository or YFinanceOptionsRepository()
        self.session = session or Session(impersonate="chrome")

    def get_option_expiration_dates(
        self, ticker: Annotated[str, "The symbol of the security."]
    ) -> list[OptionExpirationDate]:
        """
        Retrieve available option expiration dates for a given ticker.

        Args:
            ticker (str): The symbol of the security.

        Returns:
            list[OptionExpirationDate]: List of available expiration dates.
        """
        return self.repository.get_option_expiration_dates(ticker, session=self.session)

    def get_option_chain(
        self, ticker: Annotated[str, "The symbol of the security."], expiration: date | None = None
    ) -> OptionContractChain:
        """
        Retrieve the option contract chain for a given ticker and expiration date.

        Args:
            ticker (str): The symbol of the security.
            expiration (date | None, optional): The expiration date. If None, uses the nearest expiration.

        Returns:
            OptionContractChain: The option contract chain data.
        """
        return self.repository.get_option_chain(ticker, expiration, session=self.session)

    def get_call_options(
        self, ticker: Annotated[str, "The symbol of the security."], expiration: date | None = None
    ) -> list[CallOption] | None:
        """
        Retrieve call options for a given ticker and expiration date.

        Args:
            ticker (str): The symbol of the security.
            expiration (date | None, optional): The expiration date. If None, uses the nearest expiration.

        Returns:
            list[CallOption] | None: List of call options or None if unavailable.
        """
        return self.repository.get_call_options(ticker, expiration, session=self.session)

    def get_put_options(
        self, ticker: Annotated[str, "The symbol of the security."], expiration: date | None = None
    ) -> list[PutOption] | None:
        """
        Retrieve put options for a given ticker and expiration date.

        Args:
            ticker (str): The symbol of the security.
            expiration (date | None, optional): The expiration date. If None, uses the nearest expiration.

        Returns:
            list[PutOption] | None: List of put options or None if unavailable.
        """
        return self.repository.get_put_options(ticker, expiration, session=self.session)

    def get_options_volume_analysis(
        self, ticker: Annotated[str, "The symbol of the security."], expiration_date: str | None = None
    ) -> dict:
        """
        Retrieve options volume analysis for a given ticker and expiration date.

        Args:
            ticker (str): The symbol of the security.
            expiration_date (str | None, optional): The expiration date as a string. If None, uses the nearest expiration.

        Returns:
            dict: Volume analysis data.
        """
        return self.repository.get_options_volume_analysis(ticker, expiration_date, session=self.session)

    def get_options_by_moneyness(
        self,
        ticker: Annotated[str, "The symbol of the security."],
        expiration_date: str | None = None,
        moneyness_range: float = 0.1,
    ) -> dict:
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

    def get_options_skew(
        self, ticker: Annotated[str, "The symbol of the security."], expiration_date: str | None = None
    ) -> dict:
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
