"""
Open Markets Server

Initializes and runs the Open Markets MCP server, handling tool registration
and server lifecycle management.
"""

import logging
import sys

from mcp.server.transport_security import TransportSecuritySettings

from openmarkets.core.config import Settings, get_settings
from openmarkets.core.mcpserver import MCPServer, create_mcp

logger = logging.getLogger(__name__)


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


def run_http_server(mcp: MCPServer, settings: Settings) -> None:
    """
    Runs the MCP server using the streamable HTTP transport.

    DNS-rebinding protection is disabled because the server is expected to
    run behind a reverse proxy, where the inbound Host header varies.

    Args:
        mcp: MCP server instance.
        settings: Server settings/configuration.

    Raises:
        SystemExit: On shutdown request or unrecoverable server error.
    """
    try:
        mcp.run(
            transport="streamable-http",
            host=settings.host,
            port=settings.port,
            transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        )
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
    settings = get_settings()
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        stream=sys.stderr,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    mcp = create_mcp(settings)

    if settings.transport == "stdio":
        run_stdio_server(mcp)
    elif settings.transport == "http":
        run_http_server(mcp, settings)
    else:
        logger.error(f"Unsupported transport type: {settings.transport}")
        sys.exit(2)


if __name__ == "__main__":
    main()
