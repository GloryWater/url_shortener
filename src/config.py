"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields from .env
    )

    # Application
    app_name: str = Field(default="URL Shortener", description="Application name")
    app_version: str = Field(default="0.2.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8001, description="Server port")

    # Database - PostgreSQL
    postgres_user: str = Field(default="postgres", description="Database user")
    postgres_password: str = Field(default="postgres", description="Database password")
    postgres_host: str = Field(default="localhost", description="Database host")
    postgres_port: int = Field(default=5432, description="Database port")
    postgres_db: str = Field(default="postgres", description="Database name")
    sql_echo: bool = Field(default=False, description="Enable SQL query logging")

    # CORS
    allowed_origins: str = Field(
        default="http://localhost:5500",
        description="Allowed CORS origins (comma-separated)",
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
    def parse_allowed_origins(cls, v: str) -> str:
        """Ensure allowed_origins is a string."""
        return str(v) if v else "http://localhost:5500"

    @field_validator("slug_length")
    @classmethod
    def validate_slug_length(cls, v: int) -> int:
        """Validate slug length is within acceptable range."""
        if not 4 <= v <= 12:
            raise ValueError("Slug length must be between 4 and 12")
        return v

    @property
    def database_url(self) -> str:
        """Get async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        """Get sync PostgreSQL connection URL (for Alembic)."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
