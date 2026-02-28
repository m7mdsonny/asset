"""Application configuration from environment."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = Field(default="GACMS", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment name")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://gacms:gacms_secret@localhost:5432/gacms",
        description="Async PostgreSQL connection URL",
    )

    # JWT
    secret_key: str = Field(
        default="change-me-in-production-min-32-characters-required",
        description="JWT signing secret (min 32 chars)",
        min_length=32,
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=60, description="Token expiry minutes")

    # QR & Scan
    scan_base_url: str = Field(
        default="https://localhost:8000",
        description="Base URL for QR scan links",
    )
    qr_signing_secret: str = Field(
        default="qr-signing-secret-change-in-production",
        description="Secret for signing QR URLs",
    )

    # Storage
    upload_dir: str = Field(default="./uploads", description="Upload directory")
    pdf_output_dir: str = Field(default="./generated_pdfs", description="Generated PDF directory")
    backup_dir: str = Field(default="./backups", description="Backup output directory")

    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated CORS origins",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
