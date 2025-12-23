"""Create (or refresh) Chroma collections from JSON config."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import chromadb
from chromadb.api import ClientAPI
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from src.config.chroma_config import (
    DEFAULT_CHROMA_CONFIG_PATH,
    ChromaConfig,
    CollectionConfig,
    load_chroma_config,
)
from src.config.settings import settings
from utils.chroma_utils import populate_collection_from_tsv, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create (or refresh) Chroma collections from JSON config."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CHROMA_CONFIG_PATH,
        help="Path to Chroma collections config file (JSON). Defaults to docker/chroma/chroma.config.json.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Delete and recreate each collection before ingesting.",
    )
    return parser.parse_args()


def _ensure_source_exists(collection_cfg: CollectionConfig) -> None:
    if not collection_cfg.source_path.exists():
        raise FileNotFoundError(f"Source file not found: {collection_cfg.source_path}")


def _ensure_openai_key() -> None:
    """Ensure the OpenAI key is present in the environment for the embedding function."""

    key = settings.chroma_openai_api_key or settings.openai_api_key
    if key:
        os.environ.setdefault("CHROMA_OPENAI_API_KEY", key)
        os.environ.setdefault("OPENAI_API_KEY", key)

    if not os.getenv("CHROMA_OPENAI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OpenAI API key missing. Set CHROMA_OPENAI_API_KEY or OPENAI_API_KEY in your environment."
        )


def _create_or_refresh_collection(
    client: ClientAPI,
    collection_cfg: CollectionConfig,
    rebuild: bool,
) -> int:
    name = collection_cfg.collection_name
    metadata = collection_cfg.collection_metadata

    _ensure_source_exists(collection_cfg)
    print(f"\n==> Preparing collection '{name}'")
    print(f"    Source: {collection_cfg.source_path}")
    print(
        f"    Provider/model: {collection_cfg.provider} / {collection_cfg.embedding_model}"
    )
    if collection_cfg.variant:
        print(f"    Variant: {collection_cfg.variant}")
    print(f"    Batch size: {collection_cfg.batch_size}")

    if rebuild:
        try:
            client.delete_collection(name=name)
            print(f"Deleted existing collection '{name}'.")
        except Exception:
            # Collection may not exist yet; continue.
            pass

    _ensure_openai_key()

    embedding_fn = OpenAIEmbeddingFunction(model_name=collection_cfg.embedding_model)
    print("    Using embedding function:", collection_cfg.embedding_model, embedding_fn)

    collection = client.get_or_create_collection(
        name=name,
        metadata=metadata,
        embedding_function=embedding_fn,  # DO NOT CHANGE THIS LINE
    )

    print("    Testing embedding function with a sample query (empty)...")
    print(collection.query(query_texts=["worm"], n_results=1))

    print("    Ingesting TSV...")
    total = populate_collection_from_tsv(
        collection=collection,
        batch_size=collection_cfg.batch_size,
    )
    print("    Ingestion complete.")

    print(
        f"Collection '{name}' now has {total} records from {collection_cfg.source_path.name}."
    )

    print("    Testing embedding function with a sample query (empty)...")
    print(collection.query(query_texts=["worm"], n_results=1))

    return total


def main() -> None:
    args = parse_args()

    client: ClientAPI = chromadb.HttpClient(
        host=settings.chroma_host, port=settings.chroma_port
    )

    chroma_config: ChromaConfig = load_chroma_config(args.config)
    if not chroma_config.collections:
        print(f"No collections configured in {args.config}. Nothing to do.")
        return

    for collection_cfg in chroma_config.collections:
        _create_or_refresh_collection(
            client=client,
            collection_cfg=collection_cfg,
            rebuild=args.rebuild,
        )

    print("\n=== Collections summary ===")
    print(report(client))


if __name__ == "__main__":
    main()
