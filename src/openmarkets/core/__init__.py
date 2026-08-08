"""Core package internals.

The version is re-exported from the top-level package rather than resolved
again here; the two independent lookups had drifted to different fallback
behaviour (bare ``Exception`` versus ``PackageNotFoundError``).
"""

from openmarkets import __version__

__all__ = ["__version__"]
