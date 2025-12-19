from __future__ import annotations

import re
from pathlib import Path

from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def build_collection_name(
    source_path: str | Path,
    embedding_model: str | OpenAIEmbeddingFunction,
    provider: str | None = None,
    variant: str | None = None,
) -> str:
    """
    Derive a collection name from the source filename and embedding model.

    Pattern: <stem>__[provider__]<model>[__variant]
    - stem: filename without extension
    - provider: optional embedding provider slug
    - model: embedding model slug
    - variant: optional variant label (e.g., "default")
    """

    if isinstance(embedding_model, OpenAIEmbeddingFunction):
        embedding_model_str = embedding_model.model_name
    else:
        embedding_model_str = embedding_model

    stem = Path(source_path).stem
    parts = [_slugify(stem)]

    if provider:
        parts.append(_slugify(provider))

    parts.append(_slugify(embedding_model_str))

    if variant:
        parts.append(_slugify(variant))

    return "__".join(parts)
