from datetime import date, datetime
from typing import Any

import pandas as pd
from _typeshed import Incomplete
from requests import Response as Response
from requests import Session

from .data import YfData as YfData
from .exceptions import YFException as YFException
from .screener import screen as screen
from .utils import get_yf_logger as get_yf_logger
from .utils import log_indent_decorator as log_indent_decorator

class CalendarQuery:
    operator: Incomplete
    operands: Incomplete
    def __init__(self, operator: str, operand: list[Any] | list["CalendarQuery"]) -> None: ...
    def append(self, operand: Any) -> None: ...
    @property
    def is_empty(self) -> bool: ...
    def to_dict(self) -> dict: ...

DATE_STR_FORMAT: str
PREDEFINED_CALENDARS: Incomplete

class Calendars:
    session: Incomplete
    calendars: dict[str, pd.DataFrame]
    def __init__(
        self,
        start: str | datetime | date | None = None,
        end: str | datetime | date | None = None,
        session: Session | None = None,
    ) -> None: ...
    @log_indent_decorator
    def get_earnings_calendar(
        self,
        market_cap: float | None = None,
        filter_most_active: bool = True,
        start=None,
        end=None,
        limit: int = 12,
        offset: int = 0,
        force: bool = False,
    ) -> pd.DataFrame: ...
    @log_indent_decorator
    def get_ipo_info_calendar(
        self, start=None, end=None, limit: int = 12, offset: int = 0, force: bool = False
    ) -> pd.DataFrame: ...
    @log_indent_decorator
    def get_economic_events_calendar(
        self, start=None, end=None, limit: int = 12, offset: int = 0, force: bool = False
    ) -> pd.DataFrame: ...
    @log_indent_decorator
    def get_splits_calendar(
        self, start=None, end=None, limit: int = 12, offset: int = 0, force: bool = False
    ) -> pd.DataFrame: ...
    @property
    def earnings_calendar(self) -> pd.DataFrame: ...
    @property
    def ipo_info_calendar(self) -> pd.DataFrame: ...
    @property
    def economic_events_calendar(self) -> pd.DataFrame: ...
    @property
    def splits_calendar(self) -> pd.DataFrame: ...
