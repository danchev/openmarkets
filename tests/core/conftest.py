from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable

import pytest


class MiddlewareSpyApp:
    """Simple app stand-in that records add_middleware calls."""

    def __init__(self) -> None:
        self.middleware_calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def add_middleware(self, *args: Any, **kwargs: Any) -> None:
        self.middleware_calls.append((args, kwargs))


@dataclass(frozen=True)
class UvicornRunCall:
    host: str
    port: int


@pytest.fixture
def middleware_spy_app() -> MiddlewareSpyApp:
    return MiddlewareSpyApp()


@pytest.fixture
def make_middleware_spy_app() -> Callable[[], MiddlewareSpyApp]:
    return MiddlewareSpyApp


@pytest.fixture
def uvicorn_run_spy() -> tuple[Callable[..., None], dict[str, Any]]:
    calls: dict[str, Any] = {}

    def _run(app: Any, host: str, port: int, *args: Any, **kwargs: Any) -> None:
        calls["app"] = app
        calls["host"] = host
        calls["port"] = port
        calls["args"] = args
        calls["kwargs"] = kwargs

    return _run, calls


@pytest.fixture
def dummy_mcp(make_middleware_spy_app: Callable[[], MiddlewareSpyApp]) -> SimpleNamespace:
    return SimpleNamespace(streamable_http_app=lambda: make_middleware_spy_app())


@pytest.fixture
def preserve_server_settings():
    """Snapshot/restore openmarkets.core.server.settings mutable fields touched in tests."""

    import openmarkets.core.server as server

    snapshot = {
        "host": getattr(server.settings, "host", None),
        "port": getattr(server.settings, "port", None),
        "transport": getattr(server.settings, "transport", None),
    }

    yield

    if snapshot["host"] is not None:
        server.settings.host = snapshot["host"]
    if snapshot["port"] is not None:
        server.settings.port = snapshot["port"]
    if snapshot["transport"] is not None:
        server.settings.transport = snapshot["transport"]
