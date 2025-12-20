"""Basic settings loader stub for development."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from .env."""

    chroma_openai_api_key: str = "your-openai-api-key"
    openai_api_key: str = "your-openai-api-key"
    embeddings_provider: str = "openai"
    embeddings_model: str = "text-embedding-3-small"

    # Chroma service
    chroma_host: str = "127.0.0.1"
    chroma_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore legacy keys in existing .env files.
    )


settings = Settings()
