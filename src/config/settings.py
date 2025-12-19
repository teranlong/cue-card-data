"""Basic settings loader stub for development."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from .env."""

    openai_api_key: str = "your-openai-api-key"
    embeddings_provider: str = "openai"
    embeddings_model: str = "text-embedding-3-small"
    embeddings_api_base: str = "https://api.openai.com/v1"

    card_source_path: str = "data/source/cards.tsv"

    chroma_host: str = "127.0.0.1"
    chroma_port: int = 8000
    chroma_http_url: str = "http://127.0.0.1:8000"
    chroma_persist_path: str = "./docker/chroma/data"

    prefect_api_url: str = "http://127.0.0.1:4200/api"
    prefect_ui_url: str = "http://127.0.0.1:4200"
    prefect_work_pool: str = "cards-local-pool"
    prefect_work_queue: str = "cards-default"

    collection_provider: str = "openai"
    collection_model: str = "text-embedding-3-small"
    collection_variant: str = "default"
    default_collection_name: str = "cards__openai__text-embedding-3-small__default"

    confirm_destructive_reset: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
