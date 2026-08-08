"""Real end-to-end tests: spawn the actual server process, call a real tool,
get real data back through the full stack.

test_e2e.py in this same directory is named end-to-end but never calls a
tool - it only exercises protocol plumbing (initialize, ping, list_tools,
list_resource_templates, list_prompts, completion). Nothing in the test
suite had ever driven a request through the complete path a real client
actually uses: stdio transport -> MCP server -> tool dispatch -> service ->
repository -> a live network call to Yahoo Finance -> Pydantic
serialization -> back across the wire to the client.

Requires network access, so this is marked live like tests/live and
excluded from the default run. Run with:
    uv run pytest -m live -o addopts=""

which runs every live test in the suite, including those under tests/live.
"""

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

pytestmark = [pytest.mark.asyncio, pytest.mark.live]


async def test_call_tool_returns_real_data_through_the_full_stack(mcp_server_params: StdioServerParameters):
    """A real client, over real stdio, calling a real tool, must get back
    real data with both text and structured content populated - not a
    mock, not an in-process service call, but the actual server binary."""
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("get_fast_info", {"ticker": "AAPL"})

            assert result.is_error is False
            assert result.content
            assert result.content[0].type == "text"

            # structured_content is what the output schema exists to provide;
            # confirms the SDK's schema-driven serialization works end to end,
            # not just that some text came back.
            assert result.structured_content is not None
            assert result.structured_content["currency"] == "USD"
            assert result.structured_content["lastPrice"] > 0


async def test_call_tool_with_invalid_input_reports_error_over_the_wire(mcp_server_params: StdioServerParameters):
    """A real client must see is_error=True for a validation failure -
    exercising the Literal["period"] enum validation added in an earlier
    session at the actual protocol boundary, not just via a Client(mcp)
    in-process shortcut."""
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("get_history", {"ticker": "AAPL", "period": "not-a-real-period"})

            assert result.is_error is True
            assert "period" in result.content[0].text.lower()


async def test_call_tool_across_multiple_services_in_one_session(mcp_server_params: StdioServerParameters):
    """A single real client session must be able to call tools from
    different services back to back - stock, crypto, and an aggregate
    tool that fans out concurrently - all against real live data."""
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            stock_result = await session.call_tool("get_fast_info", {"ticker": "MSFT"})
            crypto_result = await session.call_tool("get_crypto_info", {"ticker": "BTC-USD"})
            aggregate_result = await session.call_tool("get_full_analysis", {"ticker": "MSFT"})

            assert stock_result.is_error is False
            assert crypto_result.is_error is False
            assert aggregate_result.is_error is False

            assert stock_result.structured_content["currency"] == "USD"
            assert crypto_result.structured_content["currency"] == "USD"
            assert "recommendations" in aggregate_result.structured_content


async def test_call_tool_for_a_previously_broken_case_end_to_end(mcp_server_params: StdioServerParameters):
    """Regression test for the NaN/None schema bug found via tests/live in
    an earlier session, now verified through the real protocol: a company
    with a missing rating must not break the tool call over the wire."""
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("get_sector_top_companies", {"sector": "technology"})

            assert result.is_error is False
            assert isinstance(result.structured_content, dict)
