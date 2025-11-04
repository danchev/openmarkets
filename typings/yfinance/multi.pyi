import pandas as _pd
from _typeshed import Incomplete

from . import Ticker as Ticker
from . import shared as shared
from . import utils as utils
from .data import YfData as YfData

@utils.log_indent_decorator
def download(
    tickers,
    start: Incomplete | None = None,
    end: Incomplete | None = None,
    actions: bool = False,
    threads: bool = True,
    ignore_tz: Incomplete | None = None,
    group_by: str = "column",
    auto_adjust: Incomplete | None = None,
    back_adjust: bool = False,
    repair: bool = False,
    keepna: bool = False,
    progress: bool = True,
    period: str = "max",
    interval: str = "1d",
    prepost: bool = False,
    proxy=...,
    rounding: bool = False,
    timeout: int = 10,
    session: Incomplete | None = None,
    multi_level_index: bool = True,
) -> _pd.DataFrame | None: ...
