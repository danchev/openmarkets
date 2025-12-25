import runpy
from typing import get_args

from openmarkets.core import config, types
from openmarkets.core.constants import SECTORS


def test_sector_annotated_contains_expected_sectors():
    # Annotated[type, metadata] -> get_args returns (type, metadata)
    args = get_args(types.Sector)
    assert len(args) == 2
    metadata = args[1]
    assert isinstance(metadata, str)
    # Ensure at least one known sector is mentioned
    assert SECTORS[0] in metadata


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
