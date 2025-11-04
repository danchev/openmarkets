import pandas as _pd
from _typeshed import Incomplete

from ..const import SECTOR_INDUSTY_MAPPING as SECTOR_INDUSTY_MAPPING
from ..data import YfData as YfData
from ..utils import (
    dynamic_docstring as dynamic_docstring,
)
from ..utils import (
    generate_list_table_from_dict as generate_list_table_from_dict,
)
from ..utils import (
    get_yf_logger as get_yf_logger,
)
from .domain import Domain as Domain

class Sector(Domain):
    def __init__(self, key, session: Incomplete | None = None, proxy=...) -> None: ...
    @property
    def top_etfs(self) -> dict[str, str]: ...
    @property
    def top_mutual_funds(self) -> dict[str, str]: ...
    @property
    def industries(self) -> _pd.DataFrame: ...
