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
from curl_cffi.requests.exceptions import RequestException

from openmarkets.core.config import get_settings

logger = logging.getLogger(__name__)

# yfinance is scraped rather than served through a public API, so requests
# are made with a browser fingerprint.
_IMPERSONATE = "chrome"

_session: Session | None = None
_session_timeout: float | None = None
_lock = threading.Lock()


def configure_session_timeout(timeout: float) -> None:
    """Configure the timeout for the lazily-created shared HTTP session.

    Server startup resolves CLI settings before provider calls happen. This
    explicit hand-off prevents a later environment-only settings lookup from
    silently replacing a CLI-provided timeout.
    """
    if timeout <= 0:
        raise ValueError("HTTP session timeout must be positive")

    global _session, _session_timeout
    with _lock:
        if _session is not None and _session_timeout != timeout:
            try:
                _session.close()
            except Exception:
                logger.debug("Failed to close the session during timeout reconfiguration.", exc_info=True)
            _session = None
        _session_timeout = timeout


def get_session() -> Session:
    """Return the process-wide HTTP session, creating it on first use.

    ``curl_cffi`` documents its ``Session`` as thread-safe, so a single
    instance can be shared across the worker threads that the MCP server
    uses to run synchronous tool handlers.

    Returns:
        Session: The shared session.
    """
    global _session, _session_timeout
    if _session is None:
        with _lock:
            if _session is None:
                timeout = _session_timeout if _session_timeout is not None else get_settings().timeout
                _session = Session(impersonate=_IMPERSONATE, timeout=timeout)
                _session_timeout = timeout
    return _session


def close_session() -> None:
    """Close the shared session if one was created.

    Registered with :mod:`atexit` so the connection pool is released on
    interpreter shutdown. Safe to call more than once.
    """
    global _session, _session_timeout
    with _lock:
        if _session is None:
            _session_timeout = None
            return
        try:
            _session.close()
        except Exception:
            logger.debug("Failed to close the shared HTTP session.", exc_info=True)
        finally:
            _session = None
            _session_timeout = None


atexit.register(close_session)


def retry_with_backoff(
    retries: int = 3,
    initial_delay: float = 0.5,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retry_exceptions: tuple[type[Exception], ...] = (RequestException,),
):
    """Decorator to retry a function call with exponential backoff and jitter.

    Args:
        retries: Maximum number of attempts. Defaults to 3.
        initial_delay: Initial sleep duration in seconds. Defaults to 0.5.
        backoff_factor: Multiplier applied to delay after each retry. Defaults to 2.0.
        jitter: Whether to add random noise to delay. Defaults to True.
        retry_exceptions: Tuple of exceptions that trigger a retry. Defaults to (Exception,).

    Returns:
        Decorated function with automatic retry behavior.
    """
    import random
    import time
    from functools import wraps

    # Retry jitter is not a security primitive, but SystemRandom avoids
    # triggering static analyzers that correctly reject predictable PRNGs in
    # security-sensitive code paths.
    jitter_source = random.SystemRandom()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exc = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as exc:
                    last_exc = exc
                    if attempt == retries - 1:
                        break
                    sleep_time = delay * (jitter_source.uniform(0.8, 1.2) if jitter else 1.0)
                    logger.warning(
                        "Call %s failed on attempt %d/%d with %s. Retrying in %.2fs...",
                        func.__name__,
                        attempt + 1,
                        retries,
                        exc,
                        sleep_time,
                    )
                    time.sleep(sleep_time)
                    delay *= backoff_factor
            if last_exc is not None:
                raise last_exc
            raise RuntimeError(f"Unexpected retry failure in {func.__name__}")

        return wrapper

    return decorator
