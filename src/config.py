"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database connection settings."""

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    user: str = Field(default="postgres", description="Database user")
    password: str = Field(default="postgres", description="Database password")
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    db_name: str = Field(default="postgres", description="Database name")
    sql_echo: bool = Field(default=False, description="Enable SQL query logging")

    @property
    def database_url(self) -> str:
        """Get async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.db_name}"
        )

    @property
    def sync_database_url(self) -> str:
        """Get sync PostgreSQL connection URL (for Alembic)."""
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.db_name}"
        )


class AppSettings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Application
    app_name: str = Field(default="URL Shortener", description="Application name")
    app_version: str = Field(default="0.2.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # CORS
    allowed_origins: list[str] = Field(
        default=["http://localhost:5500"],
        description="Allowed CORS origins",
    )

    # Rate limiting
    rate_limit_per_minute: int = Field(
        default=60,
        description="Maximum requests per minute per IP",
    )
    rate_limit_per_hour: int = Field(
        default=1000,
        description="Maximum requests per hour per IP",
    )

    # Slug settings
    slug_length: int = Field(default=6, description="Default slug length")
    slug_max_attempts: int = Field(
        default=5,
        description="Maximum attempts to generate unique slug",
    )

    # Security
    secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for security features",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | list[str]) -> list[str]:
        """Parse comma-separated origins string to list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("slug_length")
    @classmethod
    def validate_slug_length(cls, v: int) -> int:
        """Validate slug length is within acceptable range."""
        if not 4 <= v <= 12:
            raise ValueError("Slug length must be between 4 and 12")
        return v


class Settings(BaseSettings):
    """Main settings class combining all configurations."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    @property
    def database_url(self) -> str:
        """Get database URL."""
        return self.database.database_url

    @property
    def sync_database_url(self) -> str:
        """Get sync database URL."""
        return self.database.sync_database_url


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
