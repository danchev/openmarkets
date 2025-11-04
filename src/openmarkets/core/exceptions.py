class OpenMarketsException(Exception):
    """
    Base class for all custom exceptions in OpenMarkets.
    """

    pass


class APIError(OpenMarketsException):
    """
    Exception raised for API related errors.
    """

    pass


class InvalidSymbolError(OpenMarketsException):
    """
    Exception raised for invalid symbols.
    """

    pass
