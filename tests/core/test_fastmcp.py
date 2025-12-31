from unittest import mock

import pytest

import openmarkets.core.fastmcp as fastmcp


@pytest.mark.parametrize(
    ("wrapper_method", "base_method", "args"),
    [
        ("streamable_http_app", "streamable_http_app", ()),
        ("sse_app", "sse_app", (None,)),
    ],
)
def test_cors_wrapped_apps_add_cors_middleware(monkeypatch, make_middleware_spy_app, wrapper_method, base_method, args):
    monkeypatch.setattr(
        fastmcp.FastMCP,
        base_method,
        lambda self, *a, **k: make_middleware_spy_app(),
    )

    mcp = fastmcp.FastMCPWithCORS()
    app = getattr(mcp, wrapper_method)(*args)
    assert app.middleware_calls


def test_create_mcp_registers_all(monkeypatch):
    config = mock.Mock()
    mcp_instance = mock.Mock()
    monkeypatch.setattr(fastmcp, "FastMCP", mock.Mock(return_value=mcp_instance))
    monkeypatch.setattr(fastmcp, "get_settings", mock.Mock(return_value=config))
    for svc in [
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
    ]:
        monkeypatch.setattr(getattr(fastmcp, svc), "register_tool_methods", mock.Mock())
    mcp = fastmcp.create_mcp(config)
    assert mcp is mcp_instance


def test_create_mcp_uses_get_settings_when_not_provided(monkeypatch):
    mcp_instance = mock.Mock()
    monkeypatch.setattr(fastmcp, "FastMCP", mock.Mock(return_value=mcp_instance))
    get_settings_mock = mock.Mock()
    monkeypatch.setattr(fastmcp, "get_settings", get_settings_mock)
    for svc in [
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
    ]:
        monkeypatch.setattr(getattr(fastmcp, svc), "register_tool_methods", mock.Mock())
    mcp = fastmcp.create_mcp()
    get_settings_mock.assert_called_once()
    assert mcp is mcp_instance


def test_create_mcp_register_exception(monkeypatch):
    config = mock.Mock()
    mcp_instance = mock.Mock()
    monkeypatch.setattr(fastmcp, "FastMCP", mock.Mock(return_value=mcp_instance))
    monkeypatch.setattr(fastmcp, "get_settings", mock.Mock(return_value=config))
    monkeypatch.setattr(fastmcp.analysis_service, "register_tool_methods", mock.Mock(side_effect=Exception("fail")))
    for svc in [
        "crypto_service",
        "financials_service",
        "funds_service",
        "holdings_service",
        "markets_service",
        "options_service",
        "sector_industry_service",
        "stock_service",
        "technical_analysis_service",
    ]:
        monkeypatch.setattr(getattr(fastmcp, svc), "register_tool_methods", mock.Mock())
    monkeypatch.setattr(fastmcp, "logger", mock.Mock())
    with pytest.raises(RuntimeError):
        fastmcp.create_mcp(config)
