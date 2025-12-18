"""
Open Markets Server

Initializes and runs the Open Markets MCP server, handling tool registration
and server lifecycle management.
"""

import logging
import sys

import uvicorn
from starlette.middleware.cors import CORSMiddleware

from openmarkets.core.config import Settings, get_settings
from openmarkets.core.fastmcp import FastMCP, create_mcp

logger = logging.getLogger(__name__)

settings: Settings = get_settings()
mcp: FastMCP = create_mcp(settings)


def run_stdio_server(mcp: FastMCP) -> None:
    """
    Runs the MCP server using stdio transport.

    Args:
        mcp: FastMCP server instance.

    Raises:
        Exception: If the server encounters an error during runtime.
    """
    try:
        mcp.run()
    except Exception as exc:
        logger.exception("Server encountered an error during stdio runtime.")
        raise exc


def run_http_server(mcp: FastMCP, settings: Settings) -> None:
    """
    Runs the MCP server using HTTP transport.

    Args:
        mcp: FastMCP server instance.
        settings: Server settings/configuration.

    Raises:
        Exception: If the server encounters an error during runtime.
    """
    try:
        app = mcp.streamable_http_app()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allow_origins.split(","),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        uvicorn.run(app, host=settings.host, port=settings.port)
    except KeyboardInterrupt:
        logger.info(msg="Server shutdown requested by user.")
        sys.exit(0)
    except Exception:
        logger.exception("Server encountered an error during HTTP runtime.")
        sys.exit(1)


def main() -> None:
    """
    Orchestrates the startup of the Open Markets MCP server based on transport type.

    Returns:
        None
    """
    if settings.transport == "stdio":
        run_stdio_server(mcp)
    elif settings.transport == "http":
        run_http_server(mcp, settings)
    else:
        logger.error(f"Unsupported transport type: {settings.transport}")
        sys.exit(2)


if __name__ == "__main__":
    main()
