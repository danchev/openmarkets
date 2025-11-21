from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, CliSettingsSource, PydanticBaseSettingsSource, SettingsConfigDict


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
    transport: str = Field(
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
    )
    debug: bool = Field(
        False,
        description="Enable or disable debug mode.",
    )
    timeout: float = Field(
        5.0,
        description="Default timeout (in seconds) for server operations.",
    )
    cors_allow_origins: str = Field(
        "*",
        description="Allowed origins for CORS (Cross-Origin Resource Sharing).",
    )

    model_config = SettingsConfigDict(env_file=".env")

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
            CliSettingsSource(settings_cls, cli_parse_args=True, cli_ignore_unknown_args=True),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


@lru_cache
def get_settings() -> Settings:
    """Get a cached instance of the application settings.

    Returns:
        Settings: The application settings instance.
    """
    return Settings()  # type: ignore
