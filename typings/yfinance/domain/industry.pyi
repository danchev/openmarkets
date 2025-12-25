import pandas as _pd

from .. import utils as utils
from ..config import YfConfig as YfConfig
from ..data import YfData as YfData
from .domain import Domain as Domain

class Industry(Domain):
    def __init__(self, key, session=None) -> None: ...
    @property
    def sector_key(self) -> str: ...
    @property
    def sector_name(self) -> str: ...
    @property
    def top_performing_companies(self) -> _pd.DataFrame | None: ...
    @property
    def top_growth_companies(self) -> _pd.DataFrame | None: ...
