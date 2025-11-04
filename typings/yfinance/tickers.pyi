from _typeshed import Incomplete

from . import Ticker as Ticker
from . import multi as multi
from .data import YfData as YfData
from .live import WebSocket as WebSocket

class Tickers:
    symbols: Incomplete
    tickers: Incomplete
    ws: Incomplete
    def __init__(self, tickers, session: Incomplete | None = None) -> None: ...
    def history(
        self,
        period: str = "1mo",
        interval: str = "1d",
        start: Incomplete | None = None,
        end: Incomplete | None = None,
        prepost: bool = False,
        actions: bool = True,
        auto_adjust: bool = True,
        repair: bool = False,
        proxy=...,
        threads: bool = True,
        group_by: str = "column",
        progress: bool = True,
        timeout: int = 10,
        **kwargs,
    ): ...
    def download(
        self,
        period: str = "1mo",
        interval: str = "1d",
        start: Incomplete | None = None,
        end: Incomplete | None = None,
        prepost: bool = False,
        actions: bool = True,
        auto_adjust: bool = True,
        repair: bool = False,
        proxy=...,
        threads: bool = True,
        group_by: str = "column",
        progress: bool = True,
        timeout: int = 10,
        **kwargs,
    ): ...
    def news(self): ...
    def live(self, message_handler: Incomplete | None = None, verbose: bool = True) -> None: ...
