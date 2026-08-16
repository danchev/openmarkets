import runpy
from typing import get_args

import pytest
from pydantic import ValidationError
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


def test_cli_uses_documented_kebab_case_implicit_boolean_flags():
    settings = config.get_settings(
        ("--transport", "http", "--http-auth-enabled", "--http-auth-secret", "secret", "--http-stateless")
    )
    assert settings.transport == "http"
    assert settings.http_auth_enabled is True
    assert settings.http_auth_secret == "secret"
    assert settings.http_stateless is True


def test_cli_rejects_unknown_arguments():
    with pytest.raises(SystemExit):
        config.get_settings(("--not-a-real-setting", "value"))


def test_auth_enabled_requires_nonempty_secret():
    with pytest.raises(ValidationError, match="http_auth_secret"):
        config.Settings(http_auth_enabled=True, http_auth_secret="   ")


@pytest.mark.parametrize(
    "raw",
    ["short", "a" * 31, "a" * 32 + ","],
)
def test_request_state_keys_require_nonempty_32_byte_entries(raw):
    with pytest.raises(ValidationError, match="request_state_keys"):
        config.Settings(request_state_keys=raw)


def test_request_state_keys_accept_key_ring_and_environment(monkeypatch):
    monkeypatch.setenv("OPENMARKETS_REQUEST_STATE_KEYS", "a" * 32 + ", " + "b" * 32)
    settings = config.Settings()
    assert config.parse_request_state_keys(settings.request_state_keys) == ["a" * 32, "b" * 32]
