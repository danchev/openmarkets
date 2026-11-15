# Dependency Security Implementation Plan

## Design overview

Resolve the Soup Sieve and OpenTelemetry API denial-of-service findings for all supported installs through dependency floors and Python >=3.11.5.

## Class diagram

No application type changes. Dependency relationships:

```text
OpenMarkets --> yfinance --> BeautifulSoup --> SoupSieve
OpenMarkets --> MCP --> OpenTelemetry API
OpenMarkets --> SoupSieve (security floor)
OpenMarkets --> OpenTelemetry API (security floor)
```

## Entity relationship diagram

No persisted entities change. Packaging relationships:

```text
Project 1 ---- N DependencyRequirement
DependencyRequirement N ---- 1 PackageRelease
Lockfile 1 ---- N PackageRelease
```

## Implementation steps

1. Update `pyproject.toml` to require Python >=3.11.5, soupsieve>=4.0.0, and opentelemetry-api>=1.45.2.
2. Regenerate `uv.lock` with uv 0.12.2, upgrading only affected packages.
3. Record the decision in `docs/adr/0008-parser-and-trace-security.md`.
4. Run audit, locked install, and tests; verify lowest-direct resolution and the existing CI matrix before merge.

## Verification

Run `uv lock --check`, `uv audit --locked`, and malware-checked `uv sync --locked --all-groups --all-extras --python 3.13`. Run `uv run --frozen --no-sync pytest`. CI covers Python 3.11–3.14 on Linux and Windows with locked and lowest-direct resolution. Confirm no vulnerable Soup Sieve fallback remains.
