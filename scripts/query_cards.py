"""Simple ad-hoc query against the Chroma collection."""

from __future__ import annotations

import argparse
import os
import pathlib
from collections.abc import Sequence
from pathlib import Path

import chromadb
from openai import OpenAI

from src.config.chroma_config import get_default_collection_and_source  # noqa: E402
from src.config.settings import settings  # noqa: E402

DEFAULT_CONFIG_PATH = Path("chroma.config.json")


def _require_non_empty(value: str, label: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise argparse.ArgumentTypeError(f"{label} cannot be empty.")
    return cleaned


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:  # noqa: B904
        raise argparse.ArgumentTypeError("limit must be an integer.") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("limit must be at least 1.")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the Chroma collection.")
    parser.add_argument(
        "query",
        type=lambda value: _require_non_empty(value, "query text"),
        help="Search text to query.",
    )
    parser.add_argument(
        "--collection",
        type=lambda value: _require_non_empty(value, "collection name"),
        default=None,
        help="Collection name to query (defaults to first collection in config).",
    )
    parser.add_argument(
        "--limit",
        type=_positive_int,
        default=5,
        help="Number of results to return.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to Chroma collections config file (JSON). Defaults to chroma.config.json if present.",
    )
    return parser.parse_args()


def embed_texts(openai_client: OpenAI, texts: Sequence[str]) -> list[list[float]]:
    if not texts:
        return []
    response = openai_client.embeddings.create(
        model=settings.embeddings_model,
        input=list(texts),
    )
    return [item.embedding for item in response.data]


def main() -> None:
    args = parse_args()
    query = args.query

    key = settings.chroma_openai_api_key or settings.openai_api_key
    if key:
        os.environ.setdefault("OPENAI_API_KEY", key)
        os.environ.setdefault("CHROMA_OPENAI_API_KEY", key)

    client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)

    collection_name = args.collection
    if collection_name is None:
        collection_name, _ = get_default_collection_and_source(args.config)
        if not collection_name:
            raise SystemExit(
                "No collection specified and no default found in config. "
                "Pass --collection to choose one."
            )
    elif isinstance(collection_name, str) and collection_name.isdigit():
        collections = client.list_collections()
        index_raw = int(collection_name)
        index = index_raw - 1 if index_raw > 0 else 0
        if index < 0 or index >= len(collections):
            raise SystemExit(
                f"Collection index {index_raw} is out of range (found {len(collections)} collection(s))."
            )
        collection_name = collections[index].name

    collection = client.get_collection(name=collection_name)

    result = collection.query(query_texts=[query], n_results=args.limit)

    print(f"Collection: {collection_name}")
    print(f"Query: {query}")
    ids = result.get("ids", [[]])[0]
    distances = result.get("distances", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    for rank, (card_id, dist, meta) in enumerate(
        zip(ids, distances, metadatas, strict=False), start=1
    ):
        name = meta.get("name", "unknown") if isinstance(meta, dict) else "unknown"
        print(f"{rank}. id={card_id} name={name} distance={dist}")


if __name__ == "__main__":  #
    main()
