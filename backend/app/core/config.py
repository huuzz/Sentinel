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
    password_spray_threshold: int = Field(default=5, ge=2, le=100)
    password_spray_window_seconds: int = Field(default=300, ge=30, le=3600)
    api_volume_threshold: int = Field(default=30, ge=5, le=10000)
    api_volume_window_seconds: int = Field(default=60, ge=10, le=3600)
    suspicious_success_failure_threshold: int = Field(default=5, ge=1, le=100)
    suspicious_success_window_seconds: int = Field(default=600, ge=30, le=7200)
    jwt_secret: str = Field(default="development-only-change-me-32-bytes", min_length=32)
    access_token_minutes: int = Field(default=15, ge=1, le=60)
    refresh_token_days: int = Field(default=7, ge=1, le=30)
    refresh_cookie_secure: bool = False
    ml_enabled: bool = True
    ml_model_path: str = "app/ml/artifacts/isolation_forest_v1.joblib"


@lru_cache
def get_settings() -> Settings:
    return Settings()
