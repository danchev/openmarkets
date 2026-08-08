def test_register_tool_methods_registers_only_marked_methods(
    tool_registration_service,
    mcp_tool_registry_spy,
):
    """Only methods marked with @tool are published.

    Registration previously walked dir(self) and exposed every public
    instance method, so an undecorated helper silently became a callable
    tool on a network-exposed server.
    """
    tool_registration_service.register_tool_methods(mcp_tool_registry_spy)

    assert "public" in mcp_tool_registry_spy.registered
    assert "undecorated" not in mcp_tool_registry_spy.registered
    assert "static_method" not in mcp_tool_registry_spy.registered
    assert "class_method" not in mcp_tool_registry_spy.registered
    assert "property_method" not in mcp_tool_registry_spy.registered
    assert "_private" not in mcp_tool_registry_spy.registered


def test_tool_names_reports_the_published_surface(tool_registration_service):
    """tool_names() makes the published surface reviewable without a server."""
    assert tool_registration_service.tool_names() == ["public"]
