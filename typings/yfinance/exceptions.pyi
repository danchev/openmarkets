from _typeshed import Incomplete

class YFException(Exception):
    def __init__(self, description: str = "") -> None: ...

class YFDataException(YFException): ...

class YFNotImplementedError(NotImplementedError):
    def __init__(self, method_name) -> None: ...

class YFTickerMissingError(YFException):
    rationale: Incomplete
    ticker: Incomplete
    def __init__(self, ticker, rationale) -> None: ...

class YFTzMissingError(YFTickerMissingError):
    def __init__(self, ticker) -> None: ...

class YFPricesMissingError(YFTickerMissingError):
    debug_info: Incomplete
    def __init__(self, ticker, debug_info) -> None: ...

class YFEarningsDateMissing(YFTickerMissingError):
    def __init__(self, ticker) -> None: ...

class YFInvalidPeriodError(YFException):
    ticker: Incomplete
    invalid_period: Incomplete
    valid_ranges: Incomplete
    def __init__(self, ticker, invalid_period, valid_ranges) -> None: ...

class YFRateLimitError(YFException):
    def __init__(self) -> None: ...
