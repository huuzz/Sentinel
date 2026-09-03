from functools import lru_cache
from typing import Self

from pydantic import Field, model_validator
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
    max_request_body_bytes: int = Field(default=1_048_576, ge=1024, le=10_485_760)
    auth_rate_limit: int = Field(default=10, ge=1, le=10_000)
    ingestion_rate_limit: int = Field(default=120, ge=1, le=100_000)
    ai_rate_limit: int = Field(default=10, ge=1, le=10_000)
    admin_rate_limit: int = Field(default=30, ge=1, le=10_000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3600)
    cors_allowed_origins: str = ""
    trusted_proxy_ips: str = ""

    @model_validator(mode="after")
    def validate_production(self) -> Self:
        if self.environment == "production":
            if not self.refresh_cookie_secure:
                raise ValueError("Production requires secure refresh cookies")
            if self.jwt_secret in {
                "development-only-change-me-32-bytes",
                "replace-with-at-least-32-random-characters",
            }:
                raise ValueError("Production requires a unique JWT secret")
            if any(
                not origin.startswith("https://") or "*" in origin for origin in self.cors_origins
            ):
                raise ValueError("Production CORS origins must be explicit HTTPS origins")
        if "*" in self.trusted_proxies:
            raise ValueError("Proxy trust must use explicit IP addresses")
        return self

    @property
    def cors_origins(self) -> list[str]:
        return [value.strip() for value in self.cors_allowed_origins.split(",") if value.strip()]

    @property
    def trusted_proxies(self) -> set[str]:
        return {value.strip() for value in self.trusted_proxy_ips.split(",") if value.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
