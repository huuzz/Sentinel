from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="SENTINEL_", extra="ignore", case_sensitive=False
    )

    app_name: str = "SentinelAI API"
    environment: str = "development"
    log_level: str = "INFO"
    database_url: str = Field(
        default="postgresql+asyncpg://sentinel:sentinel_dev@localhost:5432/sentinel"
    )
    brute_force_threshold: int = Field(default=10, ge=2, le=1000)
    brute_force_window_seconds: int = Field(default=120, ge=10, le=3600)
    jwt_secret: str = Field(default="development-only-change-me-32-bytes", min_length=32)
    access_token_minutes: int = Field(default=15, ge=1, le=60)
    refresh_token_days: int = Field(default=7, ge=1, le=30)
    refresh_cookie_secure: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
