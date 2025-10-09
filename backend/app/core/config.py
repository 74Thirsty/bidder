"""Application configuration using Pydantic settings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    api_v1_prefix: str = "/api/v1"
    app_name: str = "Bidder API"
    debug: bool = False

    database_url: str = Field(
        default=f"sqlite:///{Path(__file__).resolve().parent.parent / 'bidder.db'}",
        description="SQLModel compatible database URL.",
    )

    geoapify_key: Optional[str] = Field(default=None, env="GEOAPIFY_KEY")
    openweather_api_key: Optional[str] = Field(default=None, env="OPENWEATHER_API_KEY")
    bls_api_key: Optional[str] = Field(default=None, env="BLS_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached instance of :class:`Settings`."""

    return Settings()
