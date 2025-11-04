from _typeshed import Incomplete

from ..data import YfData as YfData
from ..data import utils as utils

class Market:
    market: Incomplete
    session: Incomplete
    timeout: Incomplete
    def __init__(self, market: str, session: Incomplete | None = None, proxy=..., timeout: int = 30) -> None: ...
    @property
    def status(self): ...
    @property
    def summary(self): ...
