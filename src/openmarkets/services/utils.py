import inspect
from typing import Any, Callable, Protocol, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class ToolRegistrar(Protocol):
    """
    Protocol defining the MCP-like tool registration interface.
    The .tool() method should return a decorator that registers a function as a tool handler.
    """

    def tool(self) -> Callable[[F], F]: ...


class ToolRegistrationMixin:
    """
    Mixin for automatic MCP tool registration.
    Registers all public instance methods (excluding static, class methods, properties, dunder, and private/protected methods) as MCP tool handlers.
    """

    def register_tool_methods(self, mcp: ToolRegistrar) -> None:
        """
        Register all public instance methods of the service as MCP tool handlers.

        Args:
            mcp: The MCP server instance, expected to have a .tool() decorator method.
        """
        for attr_name in dir(self):
            # Skip dunder, private/protected, and this method itself
            if attr_name.startswith("_") or attr_name == "register_tool_methods":
                continue
            # Get the unbound attribute from the class to check for method/property type
            attr = getattr(type(self), attr_name, None)
            # Skip if it's a property, staticmethod, or classmethod
            if isinstance(attr, (property, staticmethod, classmethod)):
                continue
            method = getattr(self, attr_name)
            # Only register public instance methods (bound methods)
            if inspect.ismethod(method) and method.__self__ is self:
                mcp.tool()(method)
