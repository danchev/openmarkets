# OpenMarkets API reference

OpenMarkets publishes 127 MCP tools in the `full` profile. The installed server is the source of truth for tool names, parameter constraints, and output schemas; export that contract directly instead of relying on a hand-maintained copy:

```bash
uv run openmarkets --export-schema openmarkets-tools.json
```

Use `--profile` to export a smaller surface:

```bash
uv run openmarkets --profile minimal --export-schema minimal-tools.json
```

Available profiles are `full`, `minimal`, `equities`, `quant`, `macro`, `commodities`, `forex`, `crypto`, `fixed_income`, `macroeconomics`, `sec`, and `portfolio`.

## Transport endpoints

With `--transport http`, the server exposes:

- `POST /mcp` for MCP Streamable HTTP JSON-RPC
- `GET /health` for liveness
- `GET /metrics` for Prometheus metrics

HTTP operators can set `OPENMARKETS_REQUEST_STATE_KEYS` to a comma-separated
ring of secrets (each at least 32 bytes) when replicas must verify the same
multi-round request state. `--http-stateless` is an explicit compatibility
setting for 2025-era Streamable HTTP clients; 2026 clients are sessionless by
protocol regardless of this flag. Keep DNS-rebinding protection enabled unless
the deployment boundary is a trusted reverse proxy, and configure
`--http-allowed-hosts` for every accepted Host value.

Unknown tool arguments and invalid constrained values are rejected. Provider absence is reported separately from malformed provider data, and tool output follows the exported JSON schemas.

## Current tool catalogue

The categorized overview and setup instructions are maintained on the [documentation home page](index.md).
