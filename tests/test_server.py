from unittest import mock

import pytest

import openmarkets.core.server as server


def test_main_stdio(monkeypatch):
    monkeypatch.setattr(server, "settings", mock.Mock(transport="stdio"))
    called = {}
    monkeypatch.setattr(server, "run_stdio_server", lambda mcp: called.setdefault("stdio", True))
    monkeypatch.setattr(server, "run_http_server", lambda mcp, settings: called.setdefault("http", True))
    server.main()
    assert called.get("stdio")
    assert not called.get("http")


def test_main_http(monkeypatch):
    monkeypatch.setattr(server, "settings", mock.Mock(transport="http"))
    called = {}
    monkeypatch.setattr(server, "run_stdio_server", lambda mcp: called.setdefault("stdio", True))
    monkeypatch.setattr(server, "run_http_server", lambda mcp, settings: called.setdefault("http", True))
    server.main()
    assert called.get("http")
    assert not called.get("stdio")


def test_main_invalid(monkeypatch):
    monkeypatch.setattr(server, "settings", mock.Mock(transport="invalid"))
    monkeypatch.setattr(server, "logger", mock.Mock())
    with pytest.raises(SystemExit) as excinfo:
        server.main()
    assert excinfo.value.code == 2


def test_run_stdio_server_exception(monkeypatch):
    mcp = mock.Mock()
    mcp.run.side_effect = RuntimeError("fail")
    monkeypatch.setattr(server, "logger", mock.Mock())
    with pytest.raises(RuntimeError):
        server.run_stdio_server(mcp)


def test_run_http_server_keyboard(monkeypatch):
    mcp = mock.Mock()
    app = mock.Mock()
    mcp.streamable_http_app.return_value = app
    monkeypatch.setattr(server, "uvicorn", mock.Mock())
    logger_mock = mock.Mock()
    monkeypatch.setattr(server, "logger", logger_mock)

    def raise_keyboard(*a, **kw):
        raise KeyboardInterrupt()

    app.add_middleware = mock.Mock()
    server.settings.host = "127.0.0.1"
    server.settings.port = 8000
    monkeypatch.setattr(server, "uvicorn", mock.Mock(run=raise_keyboard))
    with pytest.raises(SystemExit) as excinfo:
        server.run_http_server(mcp, server.settings)
    assert excinfo.value.code == 0
    assert logger_mock.info.called


def test_run_http_server_exception(monkeypatch):
    mcp = mock.Mock()
    app = mock.Mock()
    mcp.streamable_http_app.return_value = app
    monkeypatch.setattr(server, "uvicorn", mock.Mock())
    monkeypatch.setattr(server, "logger", mock.Mock())

    def raise_exc(*a, **kw):
        raise Exception()

    app.add_middleware = mock.Mock()
    server.settings.host = "127.0.0.1"
    server.settings.port = 8000
    monkeypatch.setattr(server, "uvicorn", mock.Mock(run=raise_exc))
    with pytest.raises(SystemExit) as excinfo:
        server.run_http_server(mcp, server.settings)
    assert excinfo.value.code == 1


def test_run_http_server_logs_exception(monkeypatch):
    mcp = mock.Mock()
    app = mock.Mock()
    mcp.streamable_http_app.return_value = app

    def raise_exc(*a, **kw):
        raise Exception()

    app.add_middleware = mock.Mock()
    server.settings.host = "127.0.0.1"
    server.settings.port = 8000
    monkeypatch.setattr(server, "uvicorn", mock.Mock(run=raise_exc))
    logger_mock = mock.Mock()
    monkeypatch.setattr(server, "logger", logger_mock)
    with pytest.raises(SystemExit):
        server.run_http_server(mcp, server.settings)
    assert logger_mock.exception.called
