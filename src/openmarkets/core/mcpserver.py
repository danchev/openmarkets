"""MCP server factory and CORS-enabled server class.

Provides the server class used by Open Markets and a factory that
registers all service tool methods against the official MCP Python SDK
(v2), where the former ``FastMCP`` class is named ``MCPServer``.
"""

import logging
from typing import Any

from mcp.server import MCPServer
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

INSTRUCTIONS = "This server allows for the integration of various market data tools."

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


class CORSMCPServer(MCPServer):
    """MCP server that adds CORS middleware to its HTTP applications.

    The SDK's ``transport_security`` settings validate the ``Origin`` and
    ``Host`` headers but do not emit ``Access-Control-*`` response
    headers. Browser-based clients need those for preflight, so CORS
    middleware is layered on top of the SDK applications.

    Allowed origins are injected at construction time rather than read
    from a module-level lookup, keeping the server's configuration
    explicit.
    """

    def __init__(self, *args: Any, allow_origins: list[str] | None = None, **kwargs: Any) -> None:
        """Initialise the server.

        Args:
            *args: Positional arguments forwarded to ``MCPServer``.
            allow_origins: Origins permitted by the CORS middleware.
                Defaults to ``["*"]`` when not supplied.
            **kwargs: Keyword arguments forwarded to ``MCPServer``.
        """
        super().__init__(*args, **kwargs)
        self._allow_origins = allow_origins if allow_origins is not None else ["*"]

    def streamable_http_app(self, **kwargs: Any) -> Starlette:
        """Return the StreamableHTTP application with CORS middleware.

        Args:
            **kwargs: Keyword arguments forwarded to the base implementation.

        Returns:
            Starlette: Application with CORS middleware configured.
        """
        application = super().streamable_http_app(**kwargs)
        self._add_cors_middleware(application)
        return application

    def sse_app(self, **kwargs: Any) -> Starlette:
        """Return the SSE application with CORS middleware.

        Args:
            **kwargs: Keyword arguments forwarded to the base implementation.

        Returns:
            Starlette: Application with CORS middleware configured.
        """
        application = super().sse_app(**kwargs)
        self._add_cors_middleware(application)
        return application

    def _add_cors_middleware(self, application: Starlette) -> None:
        """Add CORS middleware to a Starlette application.

        Args:
            application: The Starlette app to configure.
        """
        application.add_middleware(
            CORSMiddleware,
            allow_origins=self._allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def _register_all_services(tool_registrar: MCPServer) -> None:
    """Register all service tool methods with the MCP server.

    Args:
        tool_registrar: MCP server instance for tool registration.

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


def _parse_allowed_origins(cors_allow_origins: str) -> list[str]:
    """Parse a comma-separated origins string into a clean list.

    Tolerates the whitespace operators naturally add around commas
    (``"a, b"``) and trailing commas, and strips a trailing ``/`` - an
    Origin header never carries a path (RFC 6454), so a trailing slash in
    the configured value is always a typo, not a meaningful difference.
    Left uncorrected, any of these silently prevent that origin from ever
    matching a real browser's ``Origin`` header.

    Args:
        cors_allow_origins: Raw comma-separated origins setting.

    Returns:
        list[str]: Non-empty, normalised origins, in the order given with
        duplicates removed.
    """
    seen: dict[str, None] = {}
    for origin in cors_allow_origins.split(","):
        cleaned = origin.strip().rstrip("/")
        if cleaned:
            seen[cleaned] = None
    return list(seen)


def _create_server(configuration: Settings) -> MCPServer:
    """Create a new MCP server instance.

    Args:
        configuration: Application configuration settings.

    Returns:
        MCPServer: New server instance.
    """
    return CORSMCPServer(
        name=configuration.name,
        instructions=INSTRUCTIONS,
        allow_origins=_parse_allowed_origins(configuration.cors_allow_origins),
    )


def create_mcp(config: Settings | None = None) -> MCPServer:
    """Create and configure the MCP server with registered tool methods.

    Args:
        config: Application configuration settings. Uses default if None.

    Returns:
        MCPServer: Configured MCP server instance.

    Raises:
        RuntimeError: If tool registration fails.
    """
    configuration = config if config is not None else get_settings()
    server = _create_server(configuration)
    _register_all_services(server)
    return server
