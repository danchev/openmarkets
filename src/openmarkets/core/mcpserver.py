"""MCP server factory and CORS-enabled server class.

Provides the server class used by Open Markets and a factory that
registers all service tool methods against the official MCP Python SDK
(v2), where the former ``FastMCP`` class is named ``MCPServer``.
"""

import asyncio
import inspect
import logging
import time
from typing import Any

from mcp.server import MCPServer
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Route

from openmarkets.core.cache import _GLOBAL_CACHE
from openmarkets.core.config import Settings, get_settings
from openmarkets.services import (
    analysis_service,
    commodities_service,
    crypto_service,
    financials_service,
    fixed_income_service,
    forex_service,
    funds_service,
    holdings_service,
    macroeconomics_service,
    markets_service,
    options_service,
    portfolio_service,
    screener_service,
    sec_service,
    sector_industry_service,
    stock_service,
    technical_analysis_service,
)

logger = logging.getLogger(__name__)

INSTRUCTIONS = "This server allows for the integration of various market data tools."

# Collection of all services to be registered
_SERVICES = [
    analysis_service,
    commodities_service,
    crypto_service,
    financials_service,
    fixed_income_service,
    forex_service,
    funds_service,
    holdings_service,
    macroeconomics_service,
    markets_service,
    options_service,
    portfolio_service,
    screener_service,
    sec_service,
    sector_industry_service,
    stock_service,
    technical_analysis_service,
]

_SERVICE_PROFILES = {
    "full": _SERVICES,
    "minimal": [stock_service, financials_service, analysis_service, screener_service],
    "equities": [
        stock_service,
        financials_service,
        analysis_service,
        holdings_service,
        options_service,
        portfolio_service,
        screener_service,
        sec_service,
    ],
    "quant": [
        stock_service,
        technical_analysis_service,
        sector_industry_service,
        markets_service,
        crypto_service,
        funds_service,
        commodities_service,
        fixed_income_service,
        forex_service,
        macroeconomics_service,
        portfolio_service,
    ],
    "macro": [
        commodities_service,
        fixed_income_service,
        forex_service,
        markets_service,
        sector_industry_service,
        macroeconomics_service,
    ],
    "commodities": [
        commodities_service,
    ],
    "forex": [
        forex_service,
    ],
    "crypto": [
        crypto_service,
    ],
    "fixed_income": [
        fixed_income_service,
    ],
    "macroeconomics": [
        macroeconomics_service,
    ],
    "sec": [
        sec_service,
    ],
    "portfolio": [
        portfolio_service,
    ],
}


_SERVER_START_TIME = time.time()


async def _health_endpoint(request: Request) -> Response:
    return PlainTextResponse("healthy")


async def _metrics_endpoint(request: Request) -> Response:
    uptime = time.time() - _SERVER_START_TIME
    cache_size = len(_GLOBAL_CACHE._cache)
    content = (
        f"# HELP openmarkets_uptime_seconds Total server uptime in seconds\n"
        f"# TYPE openmarkets_uptime_seconds gauge\n"
        f"openmarkets_uptime_seconds {uptime:.2f}\n"
        f"# HELP openmarkets_cache_entries Total active cache entries\n"
        f"# TYPE openmarkets_cache_entries gauge\n"
        f"openmarkets_cache_entries {cache_size}\n"
    )
    return PlainTextResponse(content, media_type="text/plain; version=0.0.4")


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing Bearer token authentication on HTTP endpoints."""

    def __init__(self, app: Any, secret: str) -> None:
        super().__init__(app)
        self.secret = secret

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Exclude CORS preflight (OPTIONS), health check (/health), and metrics (/metrics)
        if request.method == "OPTIONS" or request.url.path in ("/health", "/metrics"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "message": "Missing or invalid Bearer token."},
            )

        token = auth_header.removeprefix("Bearer ").strip()
        if token != self.secret:
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "message": "Invalid authentication token."},
            )

        return await call_next(request)


class CORSMCPServer(MCPServer):
    """MCP server that adds CORS and Bearer auth middleware to its HTTP applications."""

    def __init__(
        self,
        *args: Any,
        allow_origins: list[str] | None = None,
        auth_enabled: bool = False,
        auth_secret: str = "",
        **kwargs: Any,
    ) -> None:
        """Initialise the server.

        Args:
            *args: Positional arguments forwarded to ``MCPServer``.
            allow_origins: Origins permitted by the CORS middleware.
                Defaults to ``["*"]`` when not supplied.
            auth_enabled: Whether HTTP Bearer authentication is enforced.
            auth_secret: Shared secret for Bearer token validation.
            **kwargs: Keyword arguments forwarded to ``MCPServer``.
        """
        super().__init__(*args, **kwargs)
        self._allow_origins = allow_origins if allow_origins is not None else ["*"]
        self._auth_enabled = auth_enabled
        self._auth_secret = auth_secret

    def streamable_http_app(self, **kwargs: Any) -> Starlette:
        """Return the StreamableHTTP application with auth, CORS, and metrics."""
        application = super().streamable_http_app(**kwargs)
        self._add_observability_routes(application)
        self._add_auth_middleware(application)
        self._add_cors_middleware(application)
        return application

    def sse_app(self, **kwargs: Any) -> Starlette:
        """Return the SSE application with auth, CORS, and metrics."""
        application = super().sse_app(**kwargs)
        self._add_observability_routes(application)
        self._add_auth_middleware(application)
        self._add_cors_middleware(application)
        return application

    def _add_observability_routes(self, application: Starlette) -> None:
        """Add /health and /metrics observability routes."""
        if hasattr(application, "routes"):
            application.routes.append(Route("/health", _health_endpoint, methods=["GET"]))
            application.routes.append(Route("/metrics", _metrics_endpoint, methods=["GET"]))

    def _add_auth_middleware(self, application: Starlette) -> None:
        """Add Bearer auth middleware if enabled."""
        if self._auth_enabled and self._auth_secret:
            application.add_middleware(BearerAuthMiddleware, secret=self._auth_secret)

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


def _register_all_services(tool_registrar: MCPServer, profile: str = "full") -> None:
    """Register service tool methods with the MCP server based on the selected profile.

    Args:
        tool_registrar: MCP server instance for tool registration.
        profile: Tool profile name ('full', 'minimal', 'equities', 'quant').

    Raises:
        RuntimeError: If any service registration fails.
    """
    services = _SERVICE_PROFILES.get(profile.lower(), _SERVICES)
    try:
        for service in services:
            service.register_tool_methods(tool_registrar)
        logger.info("Tool registration completed successfully for profile '%s'.", profile)
    except Exception as exception:
        logger.exception("Failed to register tools for profile '%s'.", profile)
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
        auth_enabled=configuration.http_auth_enabled,
        auth_secret=configuration.http_auth_secret,
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
    _register_all_services(server, profile=configuration.profile)
    return server


def export_schema(mcp_instance: MCPServer | None = None) -> list[dict]:
    """Export the JSON schema for all registered MCP tools.

    Args:
        mcp_instance: Optional MCPServer instance. If None, creates a default server.

    Returns:
        list[dict]: List of tool schema dictionaries.
    """
    server = mcp_instance or create_mcp()

    tools_res = server.list_tools()
    if inspect.isawaitable(tools_res):
        tools = asyncio.run(tools_res)
    else:
        tools = tools_res

    if not isinstance(tools, (list, tuple)):
        return []

    return [tool.model_dump(by_alias=True) if hasattr(tool, "model_dump") else tool for tool in tools]
