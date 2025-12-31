def test_register_tool_methods_registers_only_public_instance_methods(
    tool_registration_service,
    mcp_tool_registry_spy,
):
    tool_registration_service.register_tool_methods(mcp_tool_registry_spy)

    assert "public" in mcp_tool_registry_spy.registered
    assert "static_method" not in mcp_tool_registry_spy.registered
    assert "class_method" not in mcp_tool_registry_spy.registered
    assert "property_method" not in mcp_tool_registry_spy.registered
    assert "_private" not in mcp_tool_registry_spy.registered
