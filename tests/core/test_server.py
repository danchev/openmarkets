from unittest import mock

import pytest

import openmarkets.core.server as server


@pytest.fixture
def stub_startup(monkeypatch):
    """Stub settings and server construction for main() tests.

    Returns a callable that installs a Settings mock with the given
    transport and yields the dict recording which runner was invoked.
    """

    def _install(transport: str) -> dict[str, bool]:
        monkeypatch.setattr(
            server, "get_settings", mock.Mock(return_value=mock.Mock(transport=transport, export_schema=None))
        )
        monkeypatch.setattr(server, "create_mcp", mock.Mock(return_value=mock.Mock()))

        called: dict[str, bool] = {}
        monkeypatch.setattr(server, "run_stdio_server", lambda mcp: called.setdefault("stdio", True))
        monkeypatch.setattr(server, "run_http_server", lambda mcp, settings: called.setdefault("http", True))
        return called

    return _install


@pytest.mark.parametrize("transport", ["stdio", "http"])
def test_main_selects_transport(stub_startup, transport):
    called = stub_startup(transport)

    server.main()

    assert called.get(transport)
    other = "http" if transport == "stdio" else "stdio"
    assert not called.get(other)


def test_main_invalid(monkeypatch, stub_startup):
    stub_startup("invalid")
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


def test_run_http_server_delegates_to_sdk():
    """Transport configuration is passed to the SDK runner, not to uvicorn."""
    mcp = mock.Mock()
    settings = mock.Mock(
        host="127.0.0.1",
        port=9999,
        dns_rebinding_protection_enabled=True,
        http_allowed_hosts="127.0.0.1:*,localhost:*",
        cors_allow_origins="*",
        http_stateless=False,
    )

    server.run_http_server(mcp, settings)

    kwargs = mcp.run.call_args.kwargs
    assert kwargs["transport"] == "streamable-http"
    assert kwargs["host"] == "127.0.0.1"
    assert kwargs["port"] == 9999
    assert kwargs["transport_security"].enable_dns_rebinding_protection is True
    assert kwargs["transport_security"].allowed_hosts == ["127.0.0.1:*", "localhost:*"]
    assert kwargs["stateless_http"] is False


def test_run_http_server_can_enable_stateless_legacy_mode():
    mcp = mock.Mock()
    settings = mock.Mock(
        host="127.0.0.1",
        port=9999,
        dns_rebinding_protection_enabled=True,
        http_allowed_hosts="127.0.0.1:*,localhost:*",
        cors_allow_origins="*",
        http_stateless=True,
    )

    server.run_http_server(mcp, settings)

    assert mcp.run.call_args.kwargs["stateless_http"] is True


def test_run_http_server_keyboard(monkeypatch):
    """Verifies the except KeyboardInterrupt branch as written.

    This is not the real SIGINT/SIGTERM path: verified against a running
    server that uvicorn.Server installs its own signal handlers and exits
    via sys.exit() directly, never letting KeyboardInterrupt propagate to
    this function. This test only proves the branch behaves correctly if
    something upstream of uvicorn (our own code, or a future SDK change)
    ever raises KeyboardInterrupt directly.
    """
    mcp = mock.Mock()
    mcp.run.side_effect = KeyboardInterrupt()
    logger_mock = mock.Mock()
    monkeypatch.setattr(server, "logger", logger_mock)

    with pytest.raises(SystemExit) as excinfo:
        server.run_http_server(
            mcp,
            mock.Mock(
                host="127.0.0.1",
                port=8000,
                dns_rebinding_protection_enabled=True,
                http_allowed_hosts="127.0.0.1:*,localhost:*",
                cors_allow_origins="*",
            ),
        )

    assert excinfo.value.code == 0
    assert logger_mock.info.called


def test_run_http_server_exception(monkeypatch):
    mcp = mock.Mock()
    mcp.run.side_effect = Exception()
    logger_mock = mock.Mock()
    monkeypatch.setattr(server, "logger", logger_mock)

    with pytest.raises(SystemExit) as excinfo:
        server.run_http_server(
            mcp,
            mock.Mock(
                host="127.0.0.1",
                port=8000,
                dns_rebinding_protection_enabled=True,
                http_allowed_hosts="127.0.0.1:*,localhost:*",
                cors_allow_origins="*",
            ),
        )

    assert excinfo.value.code == 1
    assert logger_mock.exception.called


def test_main_exports_schema(monkeypatch, tmp_path):
    out_file = tmp_path / "schema.json"
    fake_settings = mock.Mock(export_schema=str(out_file), transport="stdio")
    monkeypatch.setattr(server, "get_settings", mock.Mock(return_value=fake_settings))
    monkeypatch.setattr(server, "create_mcp", mock.Mock(return_value=mock.Mock()))
    monkeypatch.setattr(server, "export_schema", mock.Mock(return_value=[{"name": "test_tool"}]))

    with pytest.raises(SystemExit) as excinfo:
        server.main()
    assert excinfo.value.code == 0
    assert out_file.exists()
    assert "test_tool" in out_file.read_text()


def test_main_exports_schema_stdout(monkeypatch, capsys):
    fake_settings = mock.Mock(export_schema="-", transport="stdio")
    monkeypatch.setattr(server, "get_settings", mock.Mock(return_value=fake_settings))
    monkeypatch.setattr(server, "create_mcp", mock.Mock(return_value=mock.Mock()))
    monkeypatch.setattr(server, "export_schema", mock.Mock(return_value=[{"name": "test_tool"}]))

    with pytest.raises(SystemExit) as excinfo:
        server.main()
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "test_tool" in captured.out
