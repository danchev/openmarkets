from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


def parse_request_state_keys(raw: str) -> list[str]:
    """Parse and validate comma-separated MCP request-state signing keys.

    The MCP SDK's AES-GCM codec requires every key to contain at least
    32 bytes of secret material.  Keeping this validation at the settings
    boundary gives operators an actionable startup error and prevents a
    partially-created server from running with an invalid key ring.
    """
    if not raw.strip():
        return []

    keys = [part.strip() for part in raw.split(",")]
    if any(not key for key in keys):
        raise ValueError("request_state_keys must not contain empty comma-separated values")
    for index, key in enumerate(keys):
        if len(key.encode("utf-8")) < 32:
            raise ValueError(f"request_state_keys entry {index} must contain at least 32 bytes")
    return keys


class Settings(BaseSettings):
    """Application configuration settings.

    This class defines the configuration options for the Open Markets Server.
    Settings can be loaded from environment variables, .env files, or CLI arguments.
    """

    name: str = Field(
        "Open Markets Server",
        description="The name of the application/server.",
    )
    environment: str = Field(
        "development",
        description="The environment in which the server is running (e.g., development, production).",
    )
    transport: Literal["stdio", "http"] = Field(
        "stdio",
        description="The transport protocol to use (e.g., stdio, http, etc.).",
    )
    host: str = Field(
        "127.0.0.1",
        description="The host address for the server.",
    )
    port: int = Field(
        8000,
        description="The port number for the server.",
        ge=1,
        le=65535,
    )
    debug: bool = Field(
        False,
        description="Enable or disable debug mode.",
    )
    timeout: float = Field(
        5.0,
        description="Default timeout (in seconds) for server operations.",
        gt=0,
    )
    cors_allow_origins: str = Field(
        "*",
        description="Allowed origins for CORS (Cross-Origin Resource Sharing).",
    )
    http_auth_enabled: bool = Field(
        False,
        description="Enable Bearer token authentication for HTTP transport.",
    )
    http_auth_secret: str = Field(
        "",
        description="Shared secret required when HTTP authentication is enabled.",
    )
    dns_rebinding_protection_enabled: bool = Field(
        True,
        description="Protect HTTP transports from DNS rebinding attacks.",
    )
    http_allowed_hosts: str = Field(
        "127.0.0.1:*,localhost:*",
        description="Comma-separated Host values allowed by HTTP DNS-rebinding protection.",
    )
    http_stateless: bool = Field(
        False,
        description=(
            "Preserve the SDK's stateless Streamable HTTP behavior for 2025-era clients; "
            "modern 2026 clients are sessionless regardless."
        ),
    )
    request_state_keys: str = Field(
        "",
        description=(
            "Comma-separated MCP request-state signing keys (each at least 32 bytes) for "
            "multi-round requests across replicas."
        ),
    )
    export_schema: str | None = Field(
        None,
        description="Path to export the MCP tool JSON schema and exit.",
    )
    profile: str = Field(
        "full",
        description="Tool profile to expose: 'full' (all tools), 'minimal', 'equities', 'quant', 'macro', 'commodities', 'forex', 'crypto', 'fixed_income', 'macroeconomics', 'sec', 'portfolio'.",
    )

    @model_validator(mode="after")
    def validate_configuration(self) -> "Settings":
        """Validate that the profile name is valid.

        Args:
        Returns:
            The validated settings.

        Raises:
            ValueError: If the profile is not recognized.
        """
        # Import here to avoid circular imports
        from openmarkets.core.mcpserver import _SERVICE_PROFILES

        if self.profile not in _SERVICE_PROFILES:
            available = ", ".join(sorted(_SERVICE_PROFILES.keys()))
            raise ValueError(f"Invalid profile '{self.profile}'. Must be one of: {available}")
        if self.http_auth_enabled and not self.http_auth_secret.strip():
            raise ValueError("http_auth_secret must be non-empty when http_auth_enabled is true")
        parse_request_state_keys(self.request_state_keys)
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OPENMARKETS_",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize the order of settings sources.

        Args:
            settings_cls: The settings class.
            init_settings: Settings from __init__ arguments.
            env_settings: Settings from environment variables.
            dotenv_settings: Settings from .env files.
            file_secret_settings: Settings from secret files.

        Returns:
            A tuple of settings sources in the desired order.
        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


@lru_cache
def get_settings(cli_args: tuple[str, ...] | None = None) -> Settings:
    """Get a cached instance of the application settings.

    Returns:
        Settings: The application settings instance.
    """
    if cli_args is None:
        return Settings()
    return Settings(
        _cli_parse_args=cli_args,
        _cli_ignore_unknown_args=False,
        _cli_kebab_case=True,
        _cli_implicit_flags=True,
    )
