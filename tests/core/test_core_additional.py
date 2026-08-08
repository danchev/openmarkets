import importlib
from importlib import metadata

import openmarkets
import openmarkets.core.mcpserver as mcpserver


def test_openmarkets_version_fallback_on_exception(monkeypatch):
    """When importlib.metadata.version raises, the package should set __version__ to 'unknown'"""
    # Make version raise a generic exception
    monkeypatch.setattr(metadata, "version", lambda name: (_ for _ in ()).throw(Exception("boom")))
    # Reload the package to re-evaluate __init__.py
    module = importlib.reload(openmarkets)
    assert module.__version__ == "unknown"


def test_core_version_fallback_on_packagenotfound(monkeypatch):
    """openmarkets.core should fall back to 'unknown' when PackageNotFoundError is raised."""
    monkeypatch.setattr(metadata, "version", lambda name: (_ for _ in ()).throw(metadata.PackageNotFoundError()))
    # Reload the submodule to re-run its top-level version lookup
    module = importlib.reload(importlib.import_module("openmarkets.core"))
    assert module.__version__ == "unknown"


class DummyApp:
    """Minimal Starlette stand-in that records add_middleware calls."""

    def __init__(self):
        self.middleware_calls = []

    def add_middleware(self, *args, **kwargs):
        self.middleware_calls.append((args, kwargs))


def test_mcpserver_streamable_http_app_adds_cors(monkeypatch):
    monkeypatch.setattr(mcpserver.MCPServer, "streamable_http_app", lambda self, **kwargs: DummyApp())

    obj = mcpserver.CORSMCPServer()
    app: DummyApp = obj.streamable_http_app()  # type: ignore[assignment]
    assert isinstance(app, DummyApp)
    assert app.middleware_calls


def test_mcpserver_sse_app_adds_cors(monkeypatch):
    monkeypatch.setattr(mcpserver.MCPServer, "sse_app", lambda self, **kwargs: DummyApp())

    obj = mcpserver.CORSMCPServer()
    app: DummyApp = obj.sse_app()  # type: ignore[assignment]
    assert isinstance(app, DummyApp)
    assert app.middleware_calls
