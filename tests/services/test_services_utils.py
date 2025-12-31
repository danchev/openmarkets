from openmarkets.services.utils import ToolRegistrationMixin


class DummyMcp:
    def __init__(self):
        self.registered = []

    def tool(self):
        def decorator(func):
            self.registered.append(func.__name__)
            return func

        return decorator


class MyService(ToolRegistrationMixin):
    def public(self):
        return "ok"

    @staticmethod
    def static_m():
        return "stat"

    @classmethod
    def cls_m(cls):
        return "cls"

    @property
    def prop(self):
        return "p"

    def _private(self):
        return "no"


def test_register_tool_methods_registers_only_public_instance_methods():
    svc = MyService()
    mcp = DummyMcp()

    svc.register_tool_methods(mcp)

    assert "public" in mcp.registered
    assert "static_m" not in mcp.registered
    assert "cls_m" not in mcp.registered
    assert "prop" not in mcp.registered
    assert "_private" not in mcp.registered
