"""Shared fixtures for integration tests."""

import os

import pytest
from mcp import StdioServerParameters


@pytest.fixture
def uv_index() -> str:
    """Get UV_INDEX environment variable for server startup."""
    return os.environ.get("UV_INDEX", "")


@pytest.fixture
def mcp_server_params(uv_index: str) -> StdioServerParameters:
    """Create StdioServerParameters for MCP server startup."""
    return StdioServerParameters(
        command="uv",
        args=["run", "openmarkets", "--transport", "stdio"],
        env={"UV_INDEX": uv_index},
    )
