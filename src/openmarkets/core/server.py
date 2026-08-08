"""
Open Markets Server

Initializes and runs the Open Markets MCP server, handling tool registration
and server lifecycle management.
"""

import inspect
import logging
import sys

import uvicorn
from mcp.server.transport_security import TransportSecuritySettings

from openmarkets.core.config import Settings, get_settings
from openmarkets.core.mcpserver import MCPServer, create_mcp

logger = logging.getLogger(__name__)

settings: Settings = get_settings()
mcp: MCPServer = create_mcp(settings)


def run_stdio_server(mcp: MCPServer) -> None:
    """
    Runs the MCP server using stdio transport.

    Args:
        mcp: MCP server instance.

    Raises:
        Exception: If the server encounters an error during runtime.
    """
    try:
        mcp.run()
    except Exception as exc:
        logger.exception("Server encountered an error during stdio runtime.")
        raise exc


def _build_http_app(mcp: MCPServer):
    """Build the streamable HTTP application for the server.

    Disables DNS-rebinding protection when the underlying implementation
    supports transport security settings (the server is expected to run
    behind a reverse proxy where the Host header varies).

    Args:
        mcp: MCP server instance.

    Returns:
        The ASGI application serving the MCP streamable HTTP transport.
    """
    kwargs = {}
    if "transport_security" in inspect.signature(mcp.streamable_http_app).parameters:
        kwargs["transport_security"] = TransportSecuritySettings(enable_dns_rebinding_protection=False)
    return mcp.streamable_http_app(**kwargs)


def run_http_server(mcp: MCPServer, settings: Settings) -> None:
    """
    Runs the MCP server using HTTP transport.

    Args:
        mcp: MCP server instance.
        settings: Server settings/configuration.

    Raises:
        SystemExit: On shutdown request or unrecoverable server error.
    """
    try:
        app = _build_http_app(mcp)
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

    Logging is directed to stderr: with stdio transport, stdout carries the
    JSON-RPC protocol stream and must not receive log output.

    Returns:
        None
    """
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        stream=sys.stderr,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    if settings.transport == "stdio":
        run_stdio_server(mcp)
    elif settings.transport == "http":
        run_http_server(mcp, settings)
    else:
        logger.error(f"Unsupported transport type: {settings.transport}")
        sys.exit(2)


if __name__ == "__main__":
    main()
