from . import cache as cache
from . import utils as utils
from .config import YfConfig as YfConfig
from .exceptions import (
    YFDataException as YFDataException,
)
from .exceptions import (
    YFException as YFException,
)
from .exceptions import (
    YFRateLimitError as YFRateLimitError,
)

cache_maxsize: int

def lru_cache_freezeargs(func): ...

class SingletonMeta(type):
    def __call__(cls, *args, **kwargs): ...

class YfData(metaclass=SingletonMeta):
    def __init__(self, session=None) -> None: ...
    @utils.log_indent_decorator
    def get(self, url, params=None, timeout: int = 30): ...
    @utils.log_indent_decorator
    def post(self, url, body=None, params=None, timeout: int = 30, data=None): ...
    @lru_cache_freezeargs
    def cache_get(self, url, params=None, timeout: int = 30): ...
    def get_raw_json(self, url, params=None, timeout: int = 30): ...
