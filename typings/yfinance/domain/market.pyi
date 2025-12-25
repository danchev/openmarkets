from _typeshed import Incomplete

from ..config import YfConfig as YfConfig
from ..data import YfData as YfData
from ..data import utils as utils
from ..exceptions import YFDataException as YFDataException

class Market:
    market: Incomplete
    session: Incomplete
    timeout: Incomplete
    def __init__(self, market: str, session=None, timeout: int = 30) -> None: ...
    @property
    def status(self): ...
    @property
    def summary(self): ...
