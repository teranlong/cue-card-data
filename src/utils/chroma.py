from __future__ import annotations

import csv
from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import Any

from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from src.config.settings import settings

# ---- Ingestion helpers -----------------------------------------------------

Row = Mapping[str, str | None]


def _chunked(iterable: Iterable[Row], size: int) -> Iterator[list[Row]]:
    batch: list[Row] = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def _load_rows(tsv_path: Path) -> Iterator[Row]:
    with tsv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        yield from reader


def _build_document_text(row: Row) -> str:
    return (
        f"{row.get('name', 'Unknown')} ({row.get('type', 'n/a')}, {row.get('rarity', 'n/a')}) - "
        f"{row.get('album', 'n/a')} / {row.get('collection', 'n/a')} #{row.get('number', 'n/a')}\n"
        f"Release: {row.get('release_date', 'n/a')} | Energy {row.get('energy', 'n/a')} | "
        f"Power {row.get('power', 'n/a')} | PPE {row.get('ppe', 'n/a')}\n"
        f"Ability: {row.get('ability_name', '')} - {row.get('ability_description', '')}\n"
        f"Tags: {row.get('tags', '')}"
    )


def populate_collection_from_tsv(
    collection: Any,
    batch_size: int = 200,
) -> int:
    """
    Populate an existing Chroma collection from a TSV file using its metadata for embedding config.

    Returns the total number of rows added.
    """

    tsv_path = Path(collection.metadata["source"])
    if not tsv_path.exists():
        raise FileNotFoundError(f"Source file not found: {tsv_path}")

    metadata = collection.metadata or {}

    total = 0
    for batch in _chunked(_load_rows(tsv_path), size=batch_size):
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []

        for idx, row in enumerate(batch, total):
            doc_id = row.get("url") or row.get("number") or f"row-{idx}"
            ids.append(str(doc_id))
            documents.append(_build_document_text(row))
            metadatas.append(
                {
                    "source": row.get("url"),
                    "name": row.get("name"),
                    "album": row.get("album"),
                    "collection": row.get("collection"),
                    "number": row.get("number"),
                    "type": row.get("type"),
                    "rarity": row.get("rarity"),
                    "release_date": row.get("release_date"),
                    "tags": row.get("tags"),
                    "embedding_model": metadata.get("embedding_model") or settings.embeddings_model,
                }
            )

        # Rely on collection's embedding_function; do not pass precomputed embeddings.
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        total += len(batch)

    return total


def build_embedding_function(
    metadata: Mapping[str, Any] | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> OpenAIEmbeddingFunction:
    """
    Build an embedding function based on collection metadata or explicit overrides.
    Currently supports OpenAI embeddings only.
    """

    metadata = metadata or {}
    provider_name = provider or metadata.get("provider") or settings.embeddings_provider
    model_name = model or metadata.get("embedding_model") or settings.embeddings_model

    if provider_name != "openai":
        raise ValueError(f"Unsupported embedding provider '{provider_name}'.")

    return OpenAIEmbeddingFunction(
        api_key=settings.openai_api_key,
        model_name=str(model_name),
    )


def get_collection_with_embedding(
    client: Any,
    name: str,
    provider: str | None = None,
    model: str | None = None,
) -> Any:
    """
    Return a Chroma collection with the appropriate embedding function attached.

    Chroma's type hints for embedding functions are currently too strict for pyright/mypy,
    so the client is typed as Any and the embedding builder handles metadata defaults.
    """

    existing_metadata: dict[str, Any] = {}
    try:
        existing_metadata = (client.get_collection(name=name).metadata) or {}
    except Exception:
        # Collection may not exist yet; fall back to configured defaults.
        existing_metadata = {}

    embedding_fn = build_embedding_function(
        metadata=existing_metadata,
        provider=provider,
        model=model,
    )

    try:
        return client.get_collection(name=name, embedding_function=embedding_fn)
    except ValueError as exc:
        # If a collection already has an embedding function configured server-side,
        # requesting a different one raises a conflict. In that case, return the
        # existing collection without overriding its embedding function.
        if "embedding function already exists" in str(exc).lower():
            return client.get_collection(name=name)
        raise
