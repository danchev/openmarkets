# OpenMarkets

OpenMarkets is a Model Context Protocol server exposing normalized financial-market data and quantitative analytics through 127 tools.

## Install and run

```bash
uvx openmarkets@latest
```

For Streamable HTTP:

```bash
uvx openmarkets@latest \
  --transport http \
  --host 0.0.0.0 \
  --port 8000 \
  --http-auth-enabled \
  --http-auth-secret "replace-with-a-secret" \
  --http-allowed-hosts "markets.example.com"
```

The MCP endpoint is `/mcp`; `/health` and `/metrics` provide operational telemetry. DNS-rebinding protection is enabled by default. Configure every externally accepted Host through `--http-allowed-hosts`.

For horizontally scaled deployments, set `OPENMARKETS_REQUEST_STATE_KEYS` to a comma-separated ring of secrets (each at least 32 bytes) so multi-round MCP requests can be verified by every replica. `--http-stateless` preserves the SDK's opt-in behavior for 2025-era Streamable HTTP clients; modern 2026 clients are sessionless regardless.

## Tool profiles

| Profile | Scope |
|---|---|
| `full` | All 127 tools |
| `minimal` | 36 stock, financial, analyst, and screener tools |
| `equities` | Equity research, holdings, options, portfolio, screener, and SEC tools |
| `quant` | Cross-asset market data and portfolio analytics |
| `macro` | Commodities, rates, FX, markets, sectors, and macroeconomics |
| Domain profiles | `commodities`, `forex`, `crypto`, `fixed_income`, `macroeconomics`, `sec`, `portfolio` |

Select a profile with `--profile`, for example:

```bash
uvx openmarkets@latest --profile portfolio
```

## API contract

Generate the exact MCP input and output schemas from the installed version:

```bash
uv run openmarkets --export-schema openmarkets-tools.json
```

See the [API reference](api.md) for transport and schema details.

## Data integrity

OpenMarkets distinguishes unavailable upstream data from malformed provider responses. Unknown arguments, invalid numerical ranges, non-finite analytics, and broken provider shapes fail explicitly rather than being converted to plausible zeroes or all-null success objects.
