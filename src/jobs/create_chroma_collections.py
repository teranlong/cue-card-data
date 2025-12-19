"""Create (or refresh) a Chroma collection from TSV data."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from src.config.settings import settings
from src.utils.chroma import populate_collection_from_tsv
from src.utils.collections import build_collection_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create (or refresh) a Chroma collection from TSV data."
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Delete and recreate the collection before ingesting.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)

    # Collection 1: Cards - small embedding model

    source_path = Path("data/source/cards_v1.tsv")
    # chromadb type hints are overly strict; treat the embedding function as dynamic.
    embedding_model: Any = OpenAIEmbeddingFunction(
        api_key=settings.openai_api_key, model_name="text-embedding-3-small"
    )
    variant = "v1"

    collection_name = build_collection_name(
        source_path=source_path,
        embedding_model=embedding_model,
        variant=variant,
    )

    metadata = {
        "source": str(source_path),
        "embedding_model": embedding_model.model_name,
        "variant": variant,
    }

    if args.rebuild:
        try:
            client.delete_collection(name=collection_name)
            print(f"Deleted existing collection '{collection_name}'")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=collection_name, metadata=metadata, embedding_function=embedding_model
    )

    total = populate_collection_from_tsv(
        collection=collection,
        batch_size=200,
    )

    print(
        f"Collection '{collection_name}' now has {total} records from {source_path.name}."
    )


if __name__ == "__main__":
    main()
