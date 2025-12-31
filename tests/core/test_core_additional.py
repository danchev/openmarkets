import importlib
import types
from importlib import metadata

import openmarkets
import openmarkets.core.fastmcp as fastmcp
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


def test_fastmcp_streamable_http_app_adds_cors(monkeypatch):
    class DummyApp:
        def __init__(self):
            self.middleware_calls = []

        def add_middleware(self, *args, **kwargs):
            self.middleware_calls.append((args, kwargs))

    monkeypatch.setattr(fastmcp.FastMCP, "streamable_http_app", lambda self: DummyApp())

    obj = fastmcp.FastMCPWithCORS()
    app: DummyApp = obj.streamable_http_app()  # type: ignore[arg-type]
    assert isinstance(app, DummyApp)
    assert app.middleware_calls


def test_fastmcp_sse_app_adds_cors(monkeypatch):
    class DummyApp:
        def __init__(self):
            self.middleware_calls = []

        def add_middleware(self, *args, **kwargs):
            self.middleware_calls.append((args, kwargs))

    monkeypatch.setattr(fastmcp.FastMCP, "sse_app", lambda self, mount_path=None: DummyApp())

    obj = fastmcp.FastMCPWithCORS()
    app: DummyApp = obj.sse_app()  # type: ignore[arg-type]
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
