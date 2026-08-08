import importlib
import types
from importlib import metadata

import openmarkets
import openmarkets.core.mcpserver as mcpserver
import openmarkets.core.server as server


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


def test_server_run_http_success(monkeypatch, dummy_mcp, uvicorn_run_spy, preserve_server_settings):
    """Ensure that when uvicorn.run succeeds, no SystemExit is raised and the call is made with expected args."""
    run, calls = uvicorn_run_spy
    monkeypatch.setattr(server, "uvicorn", types.SimpleNamespace(run=run))
    # Ensure settings are set
    server.settings.host = "127.0.0.1"
    server.settings.port = 9999
    # Should not raise
    server.run_http_server(dummy_mcp, server.settings)

    assert calls["host"] == "127.0.0.1"
    assert calls["port"] == 9999
