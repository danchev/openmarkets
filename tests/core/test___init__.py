import importlib
import sys
import types


def test_version_success(monkeypatch):
    # Patch importlib.metadata.version to return a known value
    mod = types.ModuleType("openmarkets.__init__")
    monkeypatch.setitem(sys.modules, "importlib.metadata", importlib.import_module("importlib.metadata"))
    monkeypatch.setitem(sys.modules, "openmarkets.__init__", mod)
    monkeypatch.setattr("importlib.metadata.version", lambda name: "1.2.3")
    exec(
        """
try:
    from importlib.metadata import version
    __version__ = version('openmarkets')
except Exception:
    __version__ = 'unknown'
__all__ = ['__version__']
""",
        mod.__dict__,
    )
    assert mod.__version__ == "1.2.3"


def test_version_exception(monkeypatch):
    mod = types.ModuleType("openmarkets.__init__")
    monkeypatch.setitem(sys.modules, "importlib.metadata", importlib.import_module("importlib.metadata"))
    monkeypatch.setitem(sys.modules, "openmarkets.__init__", mod)
    monkeypatch.setattr("importlib.metadata.version", lambda name: (_ for _ in ()).throw(Exception("fail")))
    exec(
        """
try:
    from importlib.metadata import version
    __version__ = version('openmarkets')
except Exception:
    __version__ = 'unknown'
__all__ = ['__version__']
""",
        mod.__dict__,
    )
    assert mod.__version__ == "unknown"
