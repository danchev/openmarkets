---
description: 'Instructions for building Model Context Protocol (MCP) servers using the Python SDK'
applyTo: '**/*.py, **/pyproject.toml, **/requirements.txt'
---

# Python MCP Server Development

Targets the official MCP Python SDK **v2** (`mcp>=2.0.0`), which implements the
2026-07-28 protocol and also serves 2025-11-25 clients without configuration.

## Instructions

- Use **uv** for project management: `uv init mcp-server-demo` and `uv add "mcp[cli]"`
- Import the server class from `mcp.server`: `from mcp.server import MCPServer` (this
  was `FastMCP` in v1; `mcp.server.fastmcp` no longer exists)
- Use `@mcp.tool()`, `@mcp.resource()`, and `@mcp.prompt()` decorators for registration
- `@mcp.resource()` accepts an optional `security=` keyword for per-resource limits
- Type hints are mandatory - they're used for schema generation and validation
- Use Pydantic models, TypedDicts, or dataclasses for structured output
- Tools automatically return structured output when return types are compatible
- Prefer fully-required TypedDicts over `total=False` so the generated output schema is precise
- For stdio transport, use `mcp.run()` or `mcp.run(transport="stdio")`
- Transport options live on `run()`, **not** the constructor: `mcp.run(transport="streamable-http", host=..., port=..., stateless_http=True, json_response=True)`
- `mount_path` was removed; mount with `Mount("/path", mcp.streamable_http_app())` instead
- Use `Context` parameter in tools/resources to access MCP capabilities: `ctx: Context`
- `get_context()` was removed - declare `ctx: Context` as a parameter instead
- `ctx.fastmcp` is now `ctx.mcp_server`
- Send logs with `await ctx.debug()`, `await ctx.info()`, `await ctx.warning()`, `await ctx.error()`
- Report progress with `await ctx.report_progress(progress, total, message)`
- Request user input with the `Resolve`/`Elicit` pattern (works across both protocol eras)
- Python attributes are snake_case (`is_error`, `input_schema`, `next_cursor`); the JSON wire format stays camelCase
- Raise `MCPError(code, message, data)` for protocol-level errors; note this is *not* visible to the model. Return a normal error string/result for anything the model should read
- Configure icons with `Icon(src="path", mime_type="image/png")` (snake_case in v2)
- Use `Image` class for automatic image handling: `return Image(data=bytes, format="png")`
- Define resource templates with URI patterns: `@mcp.resource("greeting://{name}")`
- URI templates follow RFC 6570 strictly (`{+path}`, `{?query}`); path traversal is rejected by default
- Use lifespan context managers for startup/shutdown with shared resources
- Under streamable HTTP the lifespan now runs **once at startup** and is shared across all
  sessions - acquire per-connection resources inside handler bodies, not the lifespan
- Access lifespan context in tools via `ctx.request_context.lifespan_context`
- Sync (`def`) handlers run on worker threads, so they no longer block the event loop -
  but they also no longer run on the event-loop thread, which matters for thread-affine code
- Test servers with: `uv run mcp dev server.py` (Inspector) or `uv run mcp install server.py` (Claude Desktop)
- Configure CORS middleware for browser clients; `transport_security` only *validates*
  Origin/Host headers and does not emit `Access-Control-*` response headers
- Use the low-level `Server` class for maximum control; in v2 its handlers are passed as
  constructor arguments (`on_list_tools=`, `on_call_tool=`) rather than registered by decorator
- Removed in v2: WebSocket transport, the experimental Tasks API, and the `ping` protocol method
- Roots, sampling and protocol logging are deprecated in the 2026-07-28 protocol; servers
  cannot initiate requests, so return `InputRequiredResult` instead of calling back to the client

## Best Practices

- Always use type hints - they drive schema generation and validation
- Return Pydantic models or TypedDicts for structured tool outputs
- Keep tool functions focused on single responsibilities
- Provide clear docstrings - they become tool descriptions
- Use descriptive parameter names with type hints
- Validate inputs using Pydantic Field descriptions
- Implement proper error handling with try-except blocks
- Use async functions for I/O-bound operations
- Clean up resources in lifespan context managers
- Log to stderr to avoid interfering with stdio transport (when using stdio)
- Use environment variables for configuration
- Test tools independently before LLM integration
- Consider security when exposing file system or network access
- Use structured output for machine-readable data
- Provide both content and structured data for backward compatibility

## Common Patterns

### Basic Server Setup (stdio)
```python
from mcp.server import MCPServer

mcp = MCPServer("My Server")


@mcp.tool()
def calculate(a: int, b: int, op: str) -> int:
    """Perform calculation"""
    if op == "add":
        return a + b
    return a - b


if __name__ == "__main__":
    mcp.run()  # stdio by default
```

### HTTP Server
```python
from mcp.server import MCPServer

mcp = MCPServer("My HTTP Server")


@mcp.tool()
def hello(name: str = "World") -> str:
    """Greet someone"""
    return f"Hello, {name}!"


if __name__ == "__main__":
    # Transport options belong to run(), not the constructor.
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
```

### Tool with Structured Output
```python
from pydantic import BaseModel, Field


class WeatherData(BaseModel):
    temperature: float = Field(description="Temperature in Celsius")
    condition: str
    humidity: float


@mcp.tool()
def get_weather(city: str) -> WeatherData:
    """Get weather for a city"""
    return WeatherData(temperature=22.5, condition="sunny", humidity=65.0)
```

### Dynamic Resource
```python
@mcp.resource("users://{user_id}")
def get_user(user_id: str) -> str:
    """Get user profile data"""
    return f"User {user_id} profile data"
```

### Tool with Context
```python
from mcp.server.mcpserver import Context


@mcp.tool()
async def process_data(data: str, ctx: Context) -> str:
    """Process data with logging"""
    await ctx.info(f"Processing: {data}")
    await ctx.report_progress(0.5, 1.0, "Halfway done")
    return f"Processed: {data}"
```

### Requesting User Input (Resolve / Elicit)
Replaces v1's context-based elicitation and works across both protocol eras.

```python
from typing import Annotated

from pydantic import BaseModel
from mcp.server.mcpserver import AcceptedElicitation, Elicit, ElicitationResult, Resolve


class Quantity(BaseModel):
    copies: int


async def ask_quantity() -> Elicit[Quantity]:
    return Elicit("How many copies?", Quantity)


@mcp.tool()
async def reserve(
    title: str,
    quantity: Annotated[ElicitationResult[Quantity], Resolve(ask_quantity)],
) -> str:
    """Reserve copies of a title, asking the user how many."""
    if isinstance(quantity, AcceptedElicitation):
        return f"Reserved {quantity.data.copies} copies of {title}"
    return "Cancelled"
```

### Lifespan Management
```python
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server import MCPServer
from mcp.server.mcpserver import Context


@dataclass
class AppContext:
    db: Database


@asynccontextmanager
async def app_lifespan(server: MCPServer):
    # Under streamable HTTP this runs once at startup and is shared by every
    # session, so keep per-connection state out of here.
    db = await Database.connect()
    try:
        yield AppContext(db=db)
    finally:
        await db.disconnect()


mcp = MCPServer("My App", lifespan=app_lifespan)


@mcp.tool()
def query(sql: str, ctx: Context) -> str:
    """Query database"""
    db = ctx.request_context.lifespan_context.db
    return db.execute(sql)
```

### Prompt with Messages
```python
from mcp.server.mcpserver.prompts import base


@mcp.prompt(title="Code Review")
def review_code(code: str) -> list[base.Message]:
    """Create code review prompt"""
    return [
        base.UserMessage("Review this code:"),
        base.UserMessage(code),
        base.AssistantMessage("I'll review the code for you."),
    ]
```

### Error Handling
```python
from mcp.shared.exceptions import MCPError
from mcp.types import INVALID_PARAMS


@mcp.tool()
async def risky_operation(input: str) -> str:
    """Operation that might fail"""
    if not input:
        # Protocol-level error: surfaced to the client, not to the model.
        raise MCPError(INVALID_PARAMS, "input must not be empty")
    try:
        result = await perform_operation(input)
        return f"Success: {result}"
    except Exception as e:
        # Returned as a tool result the model can read and react to.
        return f"Error: {e}"
```
