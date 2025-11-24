from unittest import mock

import pytest

import openmarkets.core.fastmcp as fastmcp


def test_streamable_http_app_adds_cors(monkeypatch):
    class DummyApp:
        def __init__(self):
            self.middleware_added = False

        def add_middleware(self, *args, **kwargs):
            self.middleware_added = True

    class DummyFastMCP(fastmcp.FastMCP):
        def streamable_http_app(self):
            return DummyApp()

    obj = fastmcp.FastMCPWithCORS()
    obj.__class__ = DummyFastMCP
    app = obj.streamable_http_app()
    assert hasattr(app, "middleware_added")


def test_sse_app_adds_cors(monkeypatch):
    class DummyApp:
        def __init__(self):
            self.middleware_added = False

        def add_middleware(self, *args, **kwargs):
            self.middleware_added = True

    class DummyFastMCP(fastmcp.FastMCP):
        def sse_app(self, mount_path=None):
            return DummyApp()

    obj = fastmcp.FastMCPWithCORS()
    obj.__class__ = DummyFastMCP
    app = obj.sse_app()
    assert hasattr(app, "middleware_added")


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
