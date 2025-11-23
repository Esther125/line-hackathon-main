"""Application configuration helpers."""
from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables."""

    app_name: str = "Cony Assistant"
    openai_api_key: str
    line_channel_access_token: str
    line_channel_secret: str
    line_api_timeout: float = 10.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance for dependency injection."""

    return Settings()
