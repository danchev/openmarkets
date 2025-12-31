"""Utility classes and mixins for service layer.

Provides reusable components for automatic MCP tool registration,
enabling services to expose their methods as MCP tools through
a declarative mixin pattern.
"""

import inspect
from typing import Any, Callable, Protocol, TypeVar

ToolDecorator = TypeVar("ToolDecorator", bound=Callable[..., Any])


class ToolRegistrar(Protocol):
    """Protocol defining the MCP-like tool registration interface.

    The tool() method should return a decorator that registers
    a function as a tool handler.
    """

    def tool(self) -> Callable[[ToolDecorator], ToolDecorator]: ...


class ToolRegistrationMixin:
    """Mixin for automatic MCP tool registration.

    Registers all public instance methods as MCP tool handlers,
    excluding static methods, class methods, properties, dunder methods,
    and private/protected methods.
    """

    def register_tool_methods(self, tool_registrar: ToolRegistrar) -> None:
        """Register all public instance methods as MCP tool handlers.

        Args:
            tool_registrar: MCP server instance with a tool() decorator method.
        """
        for attribute_name in dir(self):
            if self._should_skip_attribute(attribute_name):
                continue

            if not self._is_registrable_method(attribute_name):
                continue

            method = getattr(self, attribute_name)
            tool_registrar.tool()(method)

    def _should_skip_attribute(self, attribute_name: str) -> bool:
        """Check if an attribute should be skipped during registration.

        Args:
            attribute_name: Name of the attribute to check.

        Returns:
            True if the attribute should be skipped, False otherwise.
        """
        if attribute_name.startswith("_"):
            return True

        if attribute_name == "register_tool_methods":
            return True

        return False

    def _is_registrable_method(self, attribute_name: str) -> bool:
        """Check if an attribute is a registrable instance method.

        Args:
            attribute_name: Name of the attribute to check.

        Returns:
            True if the attribute is a public instance method, False otherwise.
        """
        class_attribute = getattr(type(self), attribute_name, None)

        if isinstance(class_attribute, (property, staticmethod, classmethod)):
            return False

        method = getattr(self, attribute_name)

        if not inspect.ismethod(method):
            return False

        if method.__self__ is not self:
            return False

        return True
