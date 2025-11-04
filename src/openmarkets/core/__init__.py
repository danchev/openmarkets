from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("openmarkets")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["__version__"]
