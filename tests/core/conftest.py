from __future__ import annotations

from typing import Any, Callable

import pytest


class MiddlewareSpyApp:
    """Simple app stand-in that records add_middleware calls."""

    def __init__(self) -> None:
        self.middleware_calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def add_middleware(self, *args: Any, **kwargs: Any) -> None:
        self.middleware_calls.append((args, kwargs))


@pytest.fixture
def make_middleware_spy_app() -> Callable[[], MiddlewareSpyApp]:
    return MiddlewareSpyApp
