"""Tests for the shared HTTP session helper."""

import gc

from curl_cffi.requests import Session

from openmarkets.core import http


def test_no_session_is_created_at_import():
    """Importing the services must not open any connection pools.

    The services are module-level singletons; when each built its own
    session in __init__ this leaked nine pools per process at import time.
    """
    http.close_session()
    gc.collect()

    import openmarkets.services  # noqa: F401  (import is the thing under test)

    live = [obj for obj in gc.get_objects() if isinstance(obj, Session)]
    assert live == []


def test_get_session_is_shared_and_lazy():
    """The session is created once on first use and reused thereafter."""
    http.close_session()

    first = http.get_session()
    second = http.get_session()

    assert first is second
    http.close_session()


def test_close_session_is_idempotent():
    """close_session may be called repeatedly and before any use."""
    http.close_session()
    http.close_session()

    http.get_session()
    http.close_session()
    http.close_session()


def test_services_share_the_session_but_honour_injection():
    """Services default to the shared session; an explicit one wins."""
    http.close_session()

    from openmarkets.services.crypto import CryptoService
    from openmarkets.services.stock import StockService

    assert StockService().session is CryptoService().session

    injected = Session(impersonate="chrome")
    try:
        assert StockService(session=injected).session is injected
    finally:
        injected.close()
        http.close_session()
