from unittest import mock

import pytest

import openmarkets.core.mcpserver as mcpserver

_SERVICE_NAMES = [
    "analysis_service",
    "crypto_service",
    "financials_service",
    "funds_service",
    "holdings_service",
    "markets_service",
    "options_service",
    "sector_industry_service",
    "stock_service",
    "technical_analysis_service",
]


def _stub_all_services(monkeypatch, *, failing: str | None = None) -> None:
    """Replace every service's register_tool_methods with a mock.

    Args:
        monkeypatch: pytest monkeypatch fixture.
        failing: Name of a service whose registration should raise.
    """
    for name in _SERVICE_NAMES:
        side_effect = Exception("fail") if name == failing else None
        monkeypatch.setattr(
            getattr(mcpserver, name),
            "register_tool_methods",
            mock.Mock(side_effect=side_effect),
        )


@pytest.mark.parametrize(
    ("wrapper_method", "base_method"),
    [
        ("streamable_http_app", "streamable_http_app"),
        ("sse_app", "sse_app"),
    ],
)
def test_cors_wrapped_apps_add_cors_middleware(monkeypatch, make_middleware_spy_app, wrapper_method, base_method):
    monkeypatch.setattr(
        mcpserver.MCPServer,
        base_method,
        lambda self, **kwargs: make_middleware_spy_app(),
    )

    mcp = mcpserver.CORSMCPServer()
    app = getattr(mcp, wrapper_method)()
    assert app.middleware_calls


def test_cors_middleware_uses_configured_origins(monkeypatch, make_middleware_spy_app):
    """Allowed origins are taken from the injected value, not a global lookup."""
    monkeypatch.setattr(
        mcpserver.MCPServer,
        "streamable_http_app",
        lambda self, **kwargs: make_middleware_spy_app(),
    )

    mcp = mcpserver.CORSMCPServer(allow_origins=["https://example.com"])
    app = mcp.streamable_http_app()

    _, kwargs = app.middleware_calls[0]
    assert kwargs["allow_origins"] == ["https://example.com"]


def test_cors_middleware_defaults_to_wildcard(monkeypatch, make_middleware_spy_app):
    monkeypatch.setattr(
        mcpserver.MCPServer,
        "streamable_http_app",
        lambda self, **kwargs: make_middleware_spy_app(),
    )

    app = mcpserver.CORSMCPServer().streamable_http_app()

    _, kwargs = app.middleware_calls[0]
    assert kwargs["allow_origins"] == ["*"]


def test_create_mcp_registers_all(monkeypatch):
    config = mock.Mock(cors_allow_origins="*")
    mcp_instance = mock.Mock()
    monkeypatch.setattr(mcpserver, "CORSMCPServer", mock.Mock(return_value=mcp_instance))
    monkeypatch.setattr(mcpserver, "get_settings", mock.Mock(return_value=config))
    _stub_all_services(monkeypatch)

    mcp = mcpserver.create_mcp(config)

    assert mcp is mcp_instance


def test_create_mcp_passes_configured_origins(monkeypatch):
    """The factory forwards settings-derived origins to the server."""
    config = mock.Mock()
    config.name = "Test Server"
    config.cors_allow_origins = "https://a.example,https://b.example"
    server_factory = mock.Mock(return_value=mock.Mock())
    monkeypatch.setattr(mcpserver, "CORSMCPServer", server_factory)
    _stub_all_services(monkeypatch)

    mcpserver.create_mcp(config)

    assert server_factory.call_args.kwargs["allow_origins"] == [
        "https://a.example",
        "https://b.example",
    ]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("*", ["*"]),
        ("https://a.example,https://b.example", ["https://a.example", "https://b.example"]),
        ("https://a.example, https://b.example", ["https://a.example", "https://b.example"]),
        ("https://a.example,", ["https://a.example"]),
        ("", []),
        (" , ", []),
    ],
)
def test_parse_allowed_origins_trims_and_drops_empty(raw, expected):
    """Whitespace around commas and trailing commas must not produce
    origins that silently fail to match a real Origin header."""
    assert mcpserver._parse_allowed_origins(raw) == expected


def test_create_mcp_uses_get_settings_when_not_provided(monkeypatch):
    mcp_instance = mock.Mock()
    monkeypatch.setattr(mcpserver, "CORSMCPServer", mock.Mock(return_value=mcp_instance))
    get_settings_mock = mock.Mock(return_value=mock.Mock(cors_allow_origins="*"))
    monkeypatch.setattr(mcpserver, "get_settings", get_settings_mock)
    _stub_all_services(monkeypatch)

    mcp = mcpserver.create_mcp()

    get_settings_mock.assert_called_once()
    assert mcp is mcp_instance


def test_create_mcp_register_exception(monkeypatch):
    config = mock.Mock(cors_allow_origins="*")
    mcp_instance = mock.Mock()
    monkeypatch.setattr(mcpserver, "CORSMCPServer", mock.Mock(return_value=mcp_instance))
    monkeypatch.setattr(mcpserver, "get_settings", mock.Mock(return_value=config))
    _stub_all_services(monkeypatch, failing="analysis_service")
    monkeypatch.setattr(mcpserver, "logger", mock.Mock())

    with pytest.raises(RuntimeError):
        mcpserver.create_mcp(config)


def test_published_tool_surface_is_explicit():
    """Every service tool is opt-in and the surface is stable.

    Guards against both a regression to reflection-based publication and an
    accidental change in the number of exposed tools.
    """
    import openmarkets.services as services

    published = {name: getattr(services, name).tool_names() for name in services.__all__}

    assert sum(len(names) for names in published.values()) == 72
    for names in published.values():
        assert names, "every service must publish at least one tool"
        assert all(name.startswith(("get_", "list_", "search_", "compare_")) for name in names)
