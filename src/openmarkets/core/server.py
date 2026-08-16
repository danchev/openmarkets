import json
import logging
import sys
from pathlib import Path

from mcp.server.transport_security import TransportSecuritySettings

from openmarkets.core.config import Settings, get_settings
from openmarkets.core.mcpserver import MCPServer, _parse_allowed_origins, create_mcp, export_schema

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

    DNS-rebinding protection is enabled by default. Operators behind a
    trusted reverse proxy may explicitly disable it through configuration.

    Under real operation, ``uvicorn.Server`` installs its own SIGINT/SIGTERM
    handlers and calls ``sys.exit()`` directly for both graceful shutdown
    and startup failures (e.g. a bind conflict) - confirmed by observing
    process exit codes against a running server, not just a mock. Neither
    case reaches this function as a catchable ``KeyboardInterrupt`` or
    ``Exception``. The handlers below remain to catch errors raised by our
    own code around the ``mcp.run()`` call (for example, before uvicorn
    starts), not as the primary path for graceful shutdown or startup
    failure reporting - uvicorn already reports both with the correct
    outcome and its own exit code.

    Args:
        mcp: MCP server instance.
        settings: Server settings/configuration.

    Raises:
        SystemExit: If our own code raises before uvicorn takes over.
    """
    dns_protection = getattr(settings, "dns_rebinding_protection_enabled", True)
    if not isinstance(dns_protection, bool):
        dns_protection = True
    stateless_http = getattr(settings, "http_stateless", False)
    if not isinstance(stateless_http, bool):
        stateless_http = False
    allowed_hosts = _parse_allowed_origins(getattr(settings, "http_allowed_hosts", "127.0.0.1:*,localhost:*"))
    cors_origins = _parse_allowed_origins(getattr(settings, "cors_allow_origins", "*"))
    allowed_origins = ["http://127.0.0.1:*", "http://localhost:*"] if "*" in cors_origins else cors_origins
    try:
        mcp.run(
            transport="streamable-http",
            host=settings.host,
            port=settings.port,
            transport_security=TransportSecuritySettings(
                enable_dns_rebinding_protection=dns_protection,
                allowed_hosts=allowed_hosts,
                allowed_origins=allowed_origins,
            ),
            stateless_http=stateless_http,
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
    settings = get_settings(tuple(sys.argv[1:]))
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        stream=sys.stderr,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    mcp = create_mcp(settings)

    if settings.export_schema:
        schema = export_schema(mcp)
        schema_json = json.dumps(schema, indent=2)
        if settings.export_schema == "-":
            print(schema_json)
        else:
            out_path = Path(settings.export_schema)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(schema_json, encoding="utf-8")
            logger.info("Exported %d tool schemas to %s", len(schema), settings.export_schema)
        sys.exit(0)

    if settings.transport == "stdio":
        run_stdio_server(mcp)
    elif settings.transport == "http":
        run_http_server(mcp, settings)
    else:
        logger.error(f"Unsupported transport type: {settings.transport}")
        sys.exit(2)


if __name__ == "__main__":
    main()
