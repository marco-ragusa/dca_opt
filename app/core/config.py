"""Application settings loaded from environment variables."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    log_level: str = "INFO"
    cache_backend: Literal["local", "redis"] = "local"
    cache_ttl_seconds: int = 300
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
