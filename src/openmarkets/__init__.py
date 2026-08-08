"""OpenMarkets: a Model Context Protocol server for financial market data."""

from importlib.metadata import version

try:
    __version__: str = version("openmarkets")
except Exception:  # pragma: no cover - importlib backends raise varied errors
    # Broad by intent: the distribution may be absent (running from a source
    # checkout) or the metadata unreadable, and neither should stop import.
    __version__ = "unknown"

__all__ = ["__version__"]
