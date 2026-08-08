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

ToolDecorator = TypeVar("ToolDecorator", bound=Callable[..., Any])

#: Attribute set on a function by :func:`tool` to mark it for publication.
_TOOL_MARKER = "__openmarkets_tool__"


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

    def tool(self) -> Callable[[ToolDecorator], ToolDecorator]: ...


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

            tool_registrar.tool()(method)

    def tool_names(self) -> list[str]:
        """Return the names of the methods this service publishes.

        Returns:
            Sorted list of published tool names.
        """
        return sorted(name for name in dir(type(self)) if is_tool(getattr(type(self), name, None)))
