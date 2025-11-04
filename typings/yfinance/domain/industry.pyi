import pandas as _pd
from _typeshed import Incomplete

from .. import utils as utils
from ..data import YfData as YfData
from .domain import Domain as Domain

class Industry(Domain):
    def __init__(self, key, session: Incomplete | None = None, proxy=...) -> None: ...
    @property
    def sector_key(self) -> str: ...
    @property
    def sector_name(self) -> str: ...
    @property
    def top_performing_companies(self) -> _pd.DataFrame | None: ...
    @property
    def top_growth_companies(self) -> _pd.DataFrame | None: ...
