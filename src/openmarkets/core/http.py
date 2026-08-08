"""Shared HTTP session management.

Provides a single lazily-created ``curl_cffi`` session shared by all
services, together with deterministic cleanup.

Each service previously created its own session in its constructor, and
because the services are module-level singletons those sessions were built
at import time and never closed - nine live connection pools per process,
leaked on shutdown. A single shared session also keeps connection reuse
effective instead of splitting it across nine pools.
"""

import atexit
import logging
import threading

from curl_cffi.requests import Session

logger = logging.getLogger(__name__)

# yfinance is scraped rather than served through a public API, so requests
# are made with a browser fingerprint.
_IMPERSONATE = "chrome"

_session: Session | None = None
_lock = threading.Lock()


def get_session() -> Session:
    """Return the process-wide HTTP session, creating it on first use.

    ``curl_cffi`` documents its ``Session`` as thread-safe, so a single
    instance can be shared across the worker threads that the MCP server
    uses to run synchronous tool handlers.

    Returns:
        Session: The shared session.
    """
    global _session
    if _session is None:
        with _lock:
            if _session is None:
                _session = Session(impersonate=_IMPERSONATE)
    return _session


def close_session() -> None:
    """Close the shared session if one was created.

    Registered with :mod:`atexit` so the connection pool is released on
    interpreter shutdown. Safe to call more than once.
    """
    global _session
    with _lock:
        if _session is None:
            return
        try:
            _session.close()
        except Exception:
            logger.debug("Failed to close the shared HTTP session.", exc_info=True)
        finally:
            _session = None


atexit.register(close_session)
