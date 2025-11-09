import importlib
import inspect
import logging
import pkgutil
from collections.abc import Callable
from types import ModuleType
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class ToolRegistrar(Protocol):
    """Protocol defining the MCP-like tool registration interface."""

    def tool(self) -> Callable[[Callable[..., Any]], None]: ...


def discover_tool_modules(package_name: str) -> list[ModuleType]:
    """
    Discover all importable modules in a package for tool registration.

    Args:
        package_name: Package name to search modules from.

    Returns:
        List of imported Python modules.
    """
    try:
        package = importlib.import_module(package_name)
    except ImportError as e:
        logger.exception(f"Failed to import tools package '{package_name}': {e}")
        return []

    if not hasattr(package, "__path__"):
        logger.error(f"Package '{package_name}' has no __path__; cannot discover modules.")
        return []

    modules = []
    for _, mod_name, _ in pkgutil.walk_packages(package.__path__, prefix=f"{package_name}."):
        if mod_name.endswith(".__init__"):
            continue
        try:
            module = importlib.import_module(mod_name)
            modules.append(module)
        except Exception as e:
            logger.warning(f"Failed to import module '{mod_name}': {e}", exc_info=True)
    return modules


def discover_tool_functions(module: ModuleType) -> list[Callable[..., Any]]:
    """
    Discover all public callable tool functions in a module.

    Args:
        module: Python module to inspect.

    Returns:
        List of functions suitable for registration.
    """
    functions = []
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or name.startswith("register"):
            continue
        functions.append(func)
    return functions


def register_tools_from_module(mcp: ToolRegistrar, module: ModuleType) -> None:
    """
    Register all public tools from a given module.

    Args:
        mcp: MCP-like object implementing `.tool()` decorator.
        module: Module containing tool functions.
    """
    module_name = getattr(module, "__name__", repr(module))
    for func in discover_tool_functions(module):
        try:
            mcp.tool()(func)
            logger.debug(f"Registered tool '{func.__name__}' from module '{module_name}'")
        except Exception as e:
            logger.warning(f"Error registering tool '{func.__name__}' from '{module_name}': {e}", exc_info=True)


def register_tools_from_package(mcp: ToolRegistrar, package_name: str) -> None:
    """
    Discover and register all tools from the specified package (toolset).
    Registers all public tool functions in all modules of the package with the MCP server.

    Args:
        mcp: MCP-like object implementing `.tool()` decorator.
        package_name: Python package (toolset) to search tools from.
    """
    modules = discover_tool_modules(package_name)
    for module in modules:
        register_tools_from_module(mcp, module)


def register_toolset(mcp: ToolRegistrar, toolset_package: str) -> None:
    """
    Alias for register_tools_from_package for clarity. Registers all tools in a toolset package.

    Args:
        mcp: MCP-like object implementing `.tool()` decorator.
        toolset_package: Python package (toolset) to search tools from.
    """
    register_tools_from_package(mcp, toolset_package)


async def register_tools_on_startup(mcp: ToolRegistrar, toolset_package: str) -> None:
    """
    Async FastAPI startup hook to register all tools in a toolset package.

    Args:
        mcp: MCP-like object implementing `.tool()` decorator.
        toolset_package: Python package (toolset) to search tools from.
    """
    logger.info(f"Starting tool registration for toolset package '{toolset_package}'...")
    register_tools_from_package(mcp, toolset_package)
    logger.info("Tool registration completed.")
