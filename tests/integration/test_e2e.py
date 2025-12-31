"""
End-to-end (E2E) test for MCP server startup and API functionality.

Usage:
    cd to the `examples/snippets` directory and run:
        uv run completion-client

This test ensures:
    - The MCP server starts via stdio without errors.
    - Resource templates and prompts can be listed.
    - Completions for at least one resource template and prompt work as expected.
    - Handles empty resource templates or prompts gracefully.
"""

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import PromptReference, ResourceTemplateReference

pytestmark = pytest.mark.asyncio


# =========================
# E2E Server Startup and API Test
# =========================


@pytest.mark.asyncio
async def test_server_starts_and_lists_resources(mcp_server_params: StdioServerParameters):
    """
    End-to-end test to verify that the MCP server starts via stdio and basic API calls
    (list_resource_templates, list_prompts, and completions) succeed without errors.

    Ensures:
    - Server starts and initializes without exceptions.
    - Resource templates and prompts can be listed.
    - Completions for at least one resource template and prompt work as expected.
    - Handles empty resource templates or prompts gracefully.
    """
    server_params = mcp_server_params

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Should not raise
            await session.initialize()

            # Ping the server
            pong = await session.send_ping()
            assert pong is not None

            # List available tools templates
            tools = await session.list_tools()
            assert hasattr(tools, "tools")
            assert isinstance(tools.tools, list)
            assert len(tools.tools) >= 60
            assert any(tool.name == "get_fast_info" for tool in tools.tools)

            # List available resource templates
            templates = await session.list_resource_templates()
            assert hasattr(templates, "resourceTemplates")
            # Accept empty, but should not error
            assert isinstance(templates.resourceTemplates, list)

            # List available prompts
            prompts = await session.list_prompts()
            assert hasattr(prompts, "prompts")
            assert isinstance(prompts.prompts, list)

            # Complete resource template arguments if available
            if templates.resourceTemplates:
                template = templates.resourceTemplates[0]
                result = await session.complete(
                    ref=ResourceTemplateReference(type="ref/resource", uri=template.uriTemplate),
                    argument={"name": "owner", "value": "model"},
                )
                assert hasattr(result, "completion")
                assert hasattr(result.completion, "values")
                assert isinstance(result.completion.values, list)

                # Complete with context - repo suggestions based on owner
                result = await session.complete(
                    ref=ResourceTemplateReference(type="ref/resource", uri=template.uriTemplate),
                    argument={"name": "repo", "value": ""},
                    context_arguments={"owner": "modelcontextprotocol"},
                )
                assert hasattr(result, "completion")
                assert hasattr(result.completion, "values")
                assert isinstance(result.completion.values, list)

            # Complete prompt arguments if available
            if prompts.prompts:
                prompt_name = prompts.prompts[0].name
                result = await session.complete(
                    ref=PromptReference(type="ref/prompt", name=prompt_name),
                    argument={"name": "style", "value": ""},
                )
                assert hasattr(result, "completion")
                assert hasattr(result.completion, "values")
                assert isinstance(result.completion.values, list)
