try:
    from importlib.metadata import version

    __version__ = version("openmarkets")
except Exception:
    __version__ = "unknown"

__all__ = ["__version__"]
