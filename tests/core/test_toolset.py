"""
Unit tests for the openmarkets.core.toolset module.

These tests cover the function-based tool registration API, including package/module discovery,
error handling, and logging. Mocks are used to simulate package/module structures and import errors.
"""

import logging
import sys
import unittest
from unittest.mock import MagicMock, patch

from openmarkets.core import toolset

# Suppress logging during tests unless specifically testing log output
logging.disable(logging.CRITICAL)


class TestToolRegistryFunctions(unittest.TestCase):
    """Unit tests for toolset tool registration and discovery logic."""

    def setUp(self):
        self.mock_mcp = MagicMock()

    def tearDown(self):
        # Clean up any mock_tools modules from sys.modules
        modules_to_remove = [m for m in sys.modules if m.startswith("mock_tools")]
        for m in modules_to_remove:
            del sys.modules[m]

    @patch("importlib.import_module")
    @patch("pkgutil.walk_packages")
    def test_register_tools_from_package_discovery_and_call(self, mock_walk_packages, mock_import_module):
        """Test that register_tools_from_package discovers and registers modules correctly."""
        # Mock package structure
        mock_walk_packages.return_value = [
            (None, "mock_tools.tool_alpha", False),
            (None, "mock_tools.tool_beta", False),
            (None, "mock_tools.__init__", False),  # Should be skipped
        ]

        # Mock modules
        mock_tool_alpha_module = MagicMock()
        mock_register_alpha_func = MagicMock()
        mock_tool_alpha_module.register_tool_alpha_tools = mock_register_alpha_func

        mock_tool_beta_module = MagicMock()
        mock_tool_beta_module.some_other_func = MagicMock()

        def import_module_side_effect(name):
            if name == "mock_tools":
                mock_pkg = MagicMock()
                mock_pkg.__path__ = ["dummy_path"]
                mock_pkg.__name__ = "mock_tools"
                return mock_pkg
            elif name == "mock_tools.tool_alpha":
                return mock_tool_alpha_module
            elif name == "mock_tools.tool_beta":
                return mock_tool_beta_module
            elif name == "mock_tools.__init__":
                return MagicMock()
            raise ImportError(f"Unexpected import: {name}")

        mock_import_module.side_effect = import_module_side_effect

        with patch.object(toolset, "register_tools_from_module", MagicMock()) as mock_register_tools_from_module:
            with patch.object(logging.getLogger("openmarkets.core.toolset"), "warning"):
                toolset.register_tools_from_package(self.mock_mcp, package_name="mock_tools")

            mock_import_module.assert_any_call("mock_tools")
            mock_import_module.assert_any_call("mock_tools.tool_alpha")
            mock_import_module.assert_any_call("mock_tools.tool_beta")
            imported_package_mock = mock_import_module.mock_calls[0].args[0]
            self.assertEqual(imported_package_mock, "mock_tools")
            mock_register_tools_from_module.assert_any_call(self.mock_mcp, mock_tool_alpha_module)
            mock_register_tools_from_module.assert_any_call(self.mock_mcp, mock_tool_beta_module)
            self.assertEqual(mock_register_tools_from_module.call_count, 2)

    @patch("importlib.import_module")
    def test_register_tools_from_package_import_error(self, mock_import_module):
        """Test that import errors are logged as exceptions."""
        mock_import_module.side_effect = ImportError("Cannot import this package")
        with patch.object(logging.getLogger("openmarkets.core.toolset"), "exception") as mock_logger_exception:
            toolset.register_tools_from_package(self.mock_mcp, package_name="non_existent_package")
            self.assertTrue(mock_logger_exception.called)

    @patch("importlib.import_module")
    def test_register_tools_from_package_is_not_a_package(self, mock_import_module):
        """Test that a non-package module triggers an error log."""
        mock_module_obj = MagicMock(spec=[])
        mock_import_module.return_value = mock_module_obj
        tools_package_name = "mock_module_not_package"
        with patch.object(logging.getLogger("openmarkets.core.toolset"), "error") as mock_logger_error:
            toolset.register_tools_from_package(self.mock_mcp, package_name=tools_package_name)
            mock_import_module.assert_called_once_with(tools_package_name)
            self.assertTrue(mock_logger_error.called)

    @patch("importlib.import_module")
    @patch("pkgutil.walk_packages")
    def test_register_tools_from_package_module_import_error_in_loop(self, mock_walk_packages, mock_import_module):
        """Test that import errors in submodules are logged as warnings."""
        tools_package_name = "my_tools_pkg"
        failing_module_name = f"{tools_package_name}.failing_module"
        mock_walk_packages.return_value = [
            (None, failing_module_name, False),
        ]
        mock_tools_pkg_obj = MagicMock()
        mock_tools_pkg_obj.__path__ = ["dummy_path"]
        mock_tools_pkg_obj.__name__ = tools_package_name

        def import_module_side_effect(name, *args, **kwargs):
            if name == tools_package_name:
                return mock_tools_pkg_obj
            elif name == failing_module_name:
                raise ImportError(f"Cannot import {failing_module_name}")
            return MagicMock()

        mock_import_module.side_effect = import_module_side_effect

        with patch.object(logging.getLogger("openmarkets.core.toolset"), "warning") as mock_logger_warning:
            toolset.register_tools_from_package(self.mock_mcp, package_name=tools_package_name)
            mock_import_module.assert_any_call(tools_package_name)
            mock_import_module.assert_any_call(failing_module_name)
            mock_walk_packages.assert_called_once_with(mock_tools_pkg_obj.__path__, prefix=f"{tools_package_name}.")
            self.assertTrue(mock_logger_warning.called)


if __name__ == "__main__":
    unittest.main()
