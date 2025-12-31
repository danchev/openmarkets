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

# Collection of all services to be registered
_SERVICES = [
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
]


class FastMCPWithCORS(FastMCP):
    """FastMCP server with CORS middleware support.

    Extends FastMCP to automatically add CORS middleware to
    streamable HTTP and SSE applications.
    """

    def streamable_http_app(self) -> Starlette:
        """Return StreamableHTTP server app with CORS middleware.

        Returns:
            Starlette: Application with CORS middleware configured.
        """
        application = super().streamable_http_app()
        self._add_cors_middleware(application)
        return application

    def sse_app(self, mount_path: str | None = None) -> Starlette:
        """Return SSE server app with CORS middleware.

        Args:
            mount_path: Optional path to mount the SSE endpoint.

        Returns:
            Starlette: Application with CORS middleware configured.
        """
        application = super().sse_app(mount_path)
        self._add_cors_middleware(application)
        return application

    def _add_cors_middleware(self, application: Starlette) -> None:
        """Add CORS middleware to a Starlette application.

        Args:
            application: The Starlette app to configure.
        """
        application.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, should set specific domains
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def _register_all_services(tool_registrar: FastMCP) -> None:
    """Register all service tool methods with the MCP server.

    Args:
        tool_registrar: FastMCP server instance for tool registration.

    Raises:
        RuntimeError: If any service registration fails.
    """
    try:
        for service in _SERVICES:
            service.register_tool_methods(tool_registrar)
        logger.info("Tool registration completed successfully.")
    except Exception as exception:
        logger.exception("Failed to register tools.")
        raise RuntimeError("Tool registration failed. See logs for details.") from exception


def _create_server(configuration: Settings) -> FastMCP:
    """Create a new FastMCP server instance.

    Args:
        configuration: Application configuration settings.

    Returns:
        FastMCP: New server instance.
    """
    return FastMCP(
        name="Open Markets Server",
        instructions="This server allows for the integration of various market data tools.",
    )


def create_mcp(config: Settings | None = None) -> FastMCP:
    """Create and configure the FastMCP server with registered tool methods.

    Args:
        config: Application configuration settings. Uses default if None.

    Returns:
        FastMCP: Configured FastMCP server instance.

    Raises:
        RuntimeError: If tool registration fails.
    """
    configuration = config if config is not None else get_settings()
    server = _create_server(configuration)
    _register_all_services(server)
    return server
