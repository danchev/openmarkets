"""Domain exceptions for OpenMarkets.

Raising these instead of returning ``{"error": ...}`` lets the MCP layer
mark the tool result with ``is_error=True``. A returned error dict is
reported to the client as a *successful* call whose body happens to
describe a failure, which a model cannot reliably distinguish from data.
"""


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


class DataUnavailableError(OpenMarketsException):
    """
    Exception raised when the upstream provider has no data for a request.

    This is distinct from an invalid request: the symbol and parameters may
    be well-formed, but the provider returned nothing usable.
    """

    pass


class ProviderContractError(APIError):
    """Raised when an upstream provider returns an unexpected data shape."""

    pass
