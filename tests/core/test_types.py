"""Tests for the shared parameter types."""

import asyncio

from openmarkets.core.mcpserver import create_mcp
from openmarkets.core.types import INTERVALS, PERIODS


def _tool_schemas() -> dict:
    mcp = create_mcp()

    async def collect():
        return {tool.name: tool.input_schema or {} for tool in await mcp.list_tools()}

    return asyncio.run(collect())


def test_period_and_interval_are_exposed_as_enums():
    """The permitted values must reach the tool schema.

    A bare `str` told the model only {"type": "string"}, so it had to guess a
    value and discover the valid set from a runtime error - or, for the stock
    and technical-analysis repositories, from an opaque upstream failure
    because they never validated at all.
    """
    schemas = _tool_schemas()

    for name in ("get_crypto_history", "get_history", "get_technical_indicators", "get_volatility_metrics"):
        period = schemas[name]["properties"]["period"]
        assert period["enum"] == list(PERIODS), name

    for name in ("get_crypto_history", "get_history"):
        interval = schemas[name]["properties"]["interval"]
        assert interval["enum"] == list(INTERVALS), name


def test_no_tool_takes_an_unconstrained_period():
    """Guards against a new tool reintroducing a bare-string period."""
    for name, schema in _tool_schemas().items():
        for field in ("period", "interval"):
            prop = schema.get("properties", {}).get(field)
            if prop is not None:
                assert "enum" in prop, f"{name}.{field} is unconstrained"
