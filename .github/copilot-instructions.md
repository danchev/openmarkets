# Copilot Instructions for OpenMarkets

## Project Overview
- **OpenMarkets** is a Model Context Protocol (MCP) server for agentic retrieval of financial data from Yahoo Finance, designed for LLM and agentic workflows (Claude, Cursor, n8n, etc).
- The codebase is modular, with a clear separation between service, repository, and schema layers. All business logic is in `src/openmarkets/services/`, data access in `src/openmarkets/repositories/`, and data models in `src/openmarkets/schemas/`.
- The server is started via `openmarkets.core.server:main`, which registers all service tools and launches the MCP server (stdio or HTTP, depending on config).

## Key Architectural Patterns
- **Service Registration:** All tool methods are registered via the `FastMCP` server in `src/openmarkets/core/fastmcp.py`. Each service (e.g., `stock_service`, `crypto_service`) exposes tool methods for MCP clients.
- **Business Logic:** Service classes (e.g., `StockService`) encapsulate business logic and mediate between MCP tool calls and repository data access.
- **Repository Pattern:** Repositories (e.g., `YFinanceStockRepository`) abstract data fetching from external APIs (mainly Yahoo Finance via `yfinance`).
- **Schema Layer:** Pydantic models in `schemas/` define all data contracts for tool inputs/outputs.
- **Extensibility:** To add a new tool, implement a method in a service, register it, and ensure the repository and schema layers are updated as needed.

## Developer Workflows
- **Build:** Use `uv build` to build the project wheel.
- **Test:**
  - `uv run pytest` (or use VS Code task: Run Tests (pytest))
  - Coverage: `uv run coverage run -m pytest && coverage report`
- **Docs:** Build docs with `uv run sphinx-build -M html docs/source docs/build`.
- **Dev Server:** For local MCP server testing, use:
  ```bash
  npx @modelcontextprotocol/inspector uvx openmarkets@latest
  ```
- **Linting/Type Checking:**
  - Ruff and Pyright are configured (see `pyproject.toml`, `pyrightconfig.json`).
  - Run `uv run ruff check .` and `uv run pyright` for static analysis.

## Project Conventions
- **Python 3.10+ required** (see `pyproject.toml`).
- **Strict type checking** is enforced (see `pyrightconfig.json`).
- **All new tools must be registered in a service and exposed via FastMCP.**
- **No direct API calls in services:** Always use repository classes for external data access.
- **Tests live in `tests/` and follow `test_*.py` naming.**
- **Optional fastmcp support**: If `fastmcp` is installed, it is used for high-performance serving.

## Integration Points
- **External APIs:** Yahoo Finance (via `yfinance`), plus optional crypto and fund data sources.
- **MCP Protocol:** All tool methods are exposed as MCP tools for agentic clients.
- **CORS:** HTTP server includes CORS middleware for web-based clients.

## Examples
- To add a new tool for ETF sector allocation:
  1. Add method to `FundsService` in `services/funds.py`.
  2. Implement data access in `repositories/funds.py`.
  3. Define schema in `schemas/funds.py`.
  4. Register tool in `fastmcp.py`.

- To run all tests with coverage:
  ```bash
  uv run coverage run -m pytest && coverage report
  ```

## Key Files/Directories
- `src/openmarkets/core/server.py` – MCP server entrypoint
- `src/openmarkets/core/fastmcp.py` – Service/tool registration
- `src/openmarkets/services/` – Business logic/tool methods
- `src/openmarkets/repositories/` – Data access
- `src/openmarkets/schemas/` – Data models
- `pyproject.toml` – Build, dependency, and tool config
- `README.md` – User/developer overview

---
For more, see the README and code comments. When in doubt, follow the service-repository-schema pattern and register new tools in FastMCP.
