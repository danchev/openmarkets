import logging

try:
    from fastmcp import FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

from openmarkets.core.config import Settings
from openmarkets.core.toolset import register_toolset

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


def create_mcp(config: Settings) -> FastMCP:
    """
    Create and configure the MCP server instance.

    Initializes the MCP server and registers all available tools
    using the ToolRegistry. Logs any errors during tool registration.

    Args:
        config (Settings): Configuration object containing tool module reference.

    Returns:
        FastMCP: Configured MCP server instance.

    Raises:
        RuntimeError: If tool registration fails.
    """
    mcp = FastMCP(
        name="Open Markets Server",
        instructions=("This server allows for the integration of various market data tools."),
    )

    try:
        register_toolset(mcp, config.toolset)
        logger.info("Tool registration completed successfully.")
    except Exception as exc:
        logger.exception("Failed to initialize ToolRegistry or register tools.")
        raise RuntimeError("Tool registration failed. See logs for details.") from exc

    return mcp
