"""Application settings shared by FastAPI, the CLI and Alembic."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="WHICH_",
        extra="ignore",
    )

    app_name: str = "WhichAI"
    debug: bool = False
    database_url: str = Field(default="sqlite:///./which.db", min_length=1)
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    request_timeout_seconds: float = Field(default=30, gt=0)
    model_api_key: SecretStr | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
