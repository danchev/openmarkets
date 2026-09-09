"""Utility classes and mixins for service layer.

Provides the ``@tool`` decorator used to mark service methods for
publication as MCP tools, and the mixin that registers them.

Publication is opt-in. Registration previously walked ``dir(self)`` and
exposed every public instance method, so any helper that was not
underscore-prefixed silently became a callable tool on a network-exposed
server. Marking methods explicitly makes the public surface reviewable.
"""

import inspect
from typing import Any, Callable, Protocol, TypeVar

from mcp.types import ToolAnnotations

ToolDecorator = TypeVar("ToolDecorator", bound=Callable[..., Any])

#: Attribute set on a function by :func:`tool` to mark it for publication.
_TOOL_MARKER = "__openmarkets_tool__"

_TITLE_ACRONYMS = {
    "10k": "10-K",
    "10q": "10-Q",
    "8k": "8-K",
    "cik": "CIK",
    "cpi": "CPI",
    "dxy": "DXY",
    "ema": "EMA",
    "eps": "EPS",
    "etf": "ETF",
    "etfs": "ETFs",
    "form4": "Form 4",
    "gdp": "GDP",
    "macd": "MACD",
    "m2": "M2",
    "pce": "PCE",
    "rsi": "RSI",
    "sec": "SEC",
    "sma": "SMA",
    "ttm": "TTM",
    "var": "VaR",
    "vix": "VIX",
    "wsj": "WSJ",
    "xbrl": "XBRL",
}


def _tool_title(tool_name: str) -> str:
    """Convert a snake_case tool identifier into a readable title."""
    return " ".join(_TITLE_ACRONYMS.get(part, part.title()) for part in tool_name.split("_"))


def _tool_description(method: Callable[..., Any]) -> str:
    """Return concise prose from a tool's full docstring.

    Preserve complete explanatory paragraphs, including material modeling
    caveats, while omitting sections duplicated by the JSON input and output
    schemas. Never cut a sentence merely to meet the directory budget.
    """
    docstring = inspect.getdoc(method) or _tool_title(method.__name__)
    selected: list[str] = []
    for paragraph in docstring.split("\n\n"):
        if paragraph.startswith(("Args:", "Returns:", "Raises:")):
            break
        normalized = " ".join(paragraph.split())
        candidate = " ".join((*selected, normalized))
        description = f"Use this tool to {candidate[0].lower()}{candidate[1:]}"
        if len(description) > 500:
            break
        selected.append(normalized)
    summary = " ".join(selected) or _tool_title(method.__name__)
    return f"Use this tool to {summary[0].lower()}{summary[1:]}"


# Every published Open Markets tool reads public provider data or performs a
# deterministic calculation over that data. None writes to an upstream system.
def _read_only_tool_annotations(tool_name: str) -> ToolAnnotations:
    """Build directory-compliant annotations for a published read-only tool.

    MCP directory reviewers require a human-readable title in addition to the
    behavioral hints.  Service method names are already stable, descriptive
    snake_case identifiers, so deriving the title keeps all 127 registrations
    consistent without maintaining a second catalog.
    """
    return ToolAnnotations(
        title=_tool_title(tool_name),
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )


def tool(method: ToolDecorator) -> ToolDecorator:
    """Mark a service method for publication as an MCP tool.

    Args:
        method: The service method to expose.

    Returns:
        The same method, marked for registration.
    """
    setattr(method, _TOOL_MARKER, True)
    return method


def is_tool(candidate: object) -> bool:
    """Report whether an object was marked by :func:`tool`.

    Args:
        candidate: Object to inspect.

    Returns:
        True if the object is marked for publication.
    """
    return getattr(candidate, _TOOL_MARKER, False) is True


class ToolRegistrar(Protocol):
    """Protocol defining the MCP-like tool registration interface.

    The tool() method should return a decorator that registers
    a function as a tool handler.
    """

    def tool(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
        annotations: ToolAnnotations | None = None,
    ) -> Callable[[ToolDecorator], ToolDecorator]: ...


class ToolRegistrationMixin:
    """Mixin that registers explicitly marked methods as MCP tools."""

    def register_tool_methods(self, tool_registrar: ToolRegistrar) -> None:
        """Register every method marked with :func:`tool`.

        Args:
            tool_registrar: MCP server instance with a tool() decorator method.
        """
        for attribute_name in dir(type(self)):
            class_attribute = getattr(type(self), attribute_name, None)
            if not is_tool(class_attribute):
                continue

            method = getattr(self, attribute_name)
            if not inspect.ismethod(method) or method.__self__ is not self:
                continue

            title = _tool_title(attribute_name)
            tool_registrar.tool(
                title=title,
                description=_tool_description(method),
                annotations=_read_only_tool_annotations(attribute_name),
            )(method)

    def tool_names(self) -> list[str]:
        """Return the names of the methods this service publishes.

        Returns:
            Sorted list of published tool names.
        """
        return sorted(name for name in dir(type(self)) if is_tool(getattr(type(self), name, None)))
