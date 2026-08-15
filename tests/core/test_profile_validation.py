"""Tests to verify the profile validation fix.

This test file validates that invalid profile names are caught
at configuration load time, preventing silent failures.
"""

import os

import pytest

from openmarkets.core.config import Settings


def test_valid_profiles_are_accepted():
    """Verify that all valid profile names are accepted."""
    valid_profiles = [
        "full",
        "minimal",
        "equities",
        "quant",
        "macro",
        "commodities",
        "forex",
        "crypto",
        "fixed_income",
        "macroeconomics",
        "sec",
        "portfolio",
    ]

    for profile in valid_profiles:
        settings = Settings(profile=profile)
        assert settings.profile == profile


def test_invalid_profile_raises_validation_error():
    """Verify that invalid profile names raise a validation error."""
    invalid_profiles = [
        "invalid",
        "typo_profile",
        "FULL",  # case-sensitive
        "full ",  # trailing space
        " full",  # leading space
        "",  # empty string
    ]

    for profile in invalid_profiles:
        with pytest.raises(ValueError) as exc_info:
            Settings(profile=profile)

        error_msg = str(exc_info.value)
        assert "Invalid profile" in error_msg
        assert profile in error_msg


def test_invalid_profile_from_env_variable_raises_error():
    """Verify that environment variable with invalid profile is caught."""
    os.environ["OPENMARKETS_PROFILE"] = "nonexistent_profile"

    try:
        with pytest.raises(ValueError) as exc_info:
            Settings()

        error_msg = str(exc_info.value)
        assert "Invalid profile" in error_msg
        assert "nonexistent_profile" in error_msg
    finally:
        del os.environ["OPENMARKETS_PROFILE"]


def test_profile_validation_error_message_shows_valid_options():
    """Verify that error message includes list of valid profiles."""
    with pytest.raises(ValueError) as exc_info:
        Settings(profile="invalid")

    error_msg = str(exc_info.value)

    # Check that at least some valid profiles are mentioned
    assert "full" in error_msg
    assert "minimal" in error_msg
    assert "Must be one of:" in error_msg or "available" in error_msg.lower()


def test_default_profile_is_valid():
    """Verify that the default profile is valid."""
    settings = Settings()
    assert settings.profile == "full"
