import logging

try:
    from fastmcp import FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

from openmarkets.core.config import Settings, get_settings
from openmarkets.services import (
    analysis_service,
    crypto_service,
    financials_service,
    funds_service,
    holdings_service,
    markets_service,
    options_service,
    sector_industry_service,
    stock_service,
    technical_analysis_service,
)

logger = logging.getLogger(__name__)


class FastMCPWithCORS(FastMCP):
    def streamable_http_app(self) -> Starlette:
        """Return StreamableHTTP server app with CORS middleware"""
        # Get the original Starlette app
        app = super().streamable_http_app()

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, should set specific domains
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        return app

    def sse_app(self, mount_path: str | None = None) -> Starlette:
        """Return SSE server app with CORS middleware"""
        # Get the original Starlette app
        app = super().sse_app(mount_path)

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, should set specific domains
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        return app


def create_mcp(config: Settings | None = None) -> FastMCP:
    """Create and configure the FastMCP server with registered tool methods.

    Args:
        config (Settings | None): Application configuration settings.
    Returns:
        FastMCP: Configured FastMCP server instance.
    """
    if config is None:
        config = get_settings()
    mcp = FastMCP(
        name="Open Markets Server",
        instructions=("This server allows for the integration of various market data tools."),
    )

    try:
        analysis_service.register_tool_methods(mcp)
        crypto_service.register_tool_methods(mcp)
        financials_service.register_tool_methods(mcp)
        funds_service.register_tool_methods(mcp)
        holdings_service.register_tool_methods(mcp)
        markets_service.register_tool_methods(mcp)
        options_service.register_tool_methods(mcp)
        sector_industry_service.register_tool_methods(mcp)
        stock_service.register_tool_methods(mcp)
        technical_analysis_service.register_tool_methods(mcp)
        logger.info("Tool registration completed successfully.")
    except Exception as exc:
        logger.exception("Failed to initialize ToolRegistry or register tools.")
        raise RuntimeError("Tool registration failed. See logs for details.") from exc

    return mcp
