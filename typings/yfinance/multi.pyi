import pandas as _pd

from . import Ticker as Ticker
from . import shared as shared
from . import utils as utils
from .config import YfConfig as YfConfig
from .data import YfData as YfData

@utils.log_indent_decorator
def download(
    tickers,
    start=None,
    end=None,
    actions: bool = False,
    threads: bool = True,
    ignore_tz=None,
    group_by: str = "column",
    auto_adjust: bool = True,
    back_adjust: bool = False,
    repair: bool = False,
    keepna: bool = False,
    progress: bool = True,
    period=None,
    interval: str = "1d",
    prepost: bool = False,
    rounding: bool = False,
    timeout: int = 10,
    session=None,
    multi_level_index: bool = True,
) -> _pd.DataFrame | None: ...
