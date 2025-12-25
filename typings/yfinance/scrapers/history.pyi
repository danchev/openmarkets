import pandas as pd
from _typeshed import Incomplete
from yfinance import shared as shared
from yfinance import utils as utils
from yfinance.config import YfConfig as YfConfig
from yfinance.exceptions import (
    YFDataException as YFDataException,
)
from yfinance.exceptions import (
    YFInvalidPeriodError as YFInvalidPeriodError,
)
from yfinance.exceptions import (
    YFPricesMissingError as YFPricesMissingError,
)
from yfinance.exceptions import (
    YFRateLimitError as YFRateLimitError,
)
from yfinance.exceptions import (
    YFTzMissingError as YFTzMissingError,
)

class PriceHistory:
    ticker: Incomplete
    tz: Incomplete
    session: Incomplete
    def __init__(self, data, ticker, tz, session=None) -> None: ...
    @utils.log_indent_decorator
    def history(
        self,
        period=None,
        interval: str = "1d",
        start=None,
        end=None,
        prepost: bool = False,
        actions: bool = True,
        auto_adjust: bool = True,
        back_adjust: bool = False,
        repair: bool = False,
        keepna: bool = False,
        rounding: bool = False,
        timeout: int = 10,
        raise_errors: bool = False,
    ) -> pd.DataFrame: ...
    def get_history_metadata(self) -> dict: ...
    def get_dividends(self, period: str = "max") -> pd.Series: ...
    def get_capital_gains(self, period: str = "max") -> pd.Series: ...
    def get_splits(self, period: str = "max") -> pd.Series: ...
    def get_actions(self, period: str = "max") -> pd.Series: ...
