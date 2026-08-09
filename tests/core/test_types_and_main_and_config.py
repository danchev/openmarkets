import runpy
from typing import get_args

from pydantic.fields import FieldInfo

from openmarkets.core import config, types
from openmarkets.core.constants import SECTORS


def test_sector_annotated_contains_expected_sectors():
    """The sector description must carry the permitted values.

    The metadata is a pydantic FieldInfo rather than a bare string: a plain
    string in Annotated[...] is ignored by schema generation, so the previous
    form never reached the generated tool definition.
    """
    args = get_args(types.Sector)
    assert len(args) == 2
    metadata = args[1]

    assert isinstance(metadata, FieldInfo)
    assert metadata.description is not None
    assert SECTORS[0] in metadata.description


def test_main_entry_calls_server_main(monkeypatch):
    called = {}

    def fake_main():
        called["ok"] = True

    monkeypatch.setattr("openmarkets.core.server.main", fake_main)
    # Execute the package as a script which should trigger __main__.py
    runpy.run_module("openmarkets", run_name="__main__")
    assert called.get("ok")


def test_get_settings_cached():
    s1 = config.get_settings()
    s2 = config.get_settings()
    assert s1 is s2


def test_settings_env_prefix_and_profile(monkeypatch):
    monkeypatch.setenv("OPENMARKETS_PORT", "9999")
    monkeypatch.setenv("OPENMARKETS_PROFILE", "minimal")
    monkeypatch.setenv("HOST", "ambient_host_to_ignore")

    settings = config.Settings()
    assert settings.port == 9999
    assert settings.profile == "minimal"
    assert settings.host == "127.0.0.1"
