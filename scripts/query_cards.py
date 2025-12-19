"""Simple ad-hoc query against the Chroma collection."""

from __future__ import annotations

import argparse
import pathlib
import sys
from collections.abc import Sequence

import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import OpenAI

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config.settings import settings  # noqa: E402
from src.utils.chroma import get_collection_with_embedding  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the Chroma collection.")
    parser.add_argument(
        "query",
        help="Search text to query.",
    )
    parser.add_argument(
        "--collection",
        default=settings.default_collection_name,
        help="Collection name to query (default: configured default).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of results to return.",
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
    openai_client = OpenAI(api_key=settings.openai_api_key, base_url=settings.embeddings_api_base)

    client = chromadb.Client(
        settings=ChromaSettings(
            chroma_api_impl="chromadb.api.fastapi.FastAPI",
            chroma_server_host=settings.chroma_host,
            chroma_server_http_port=settings.chroma_port,
            anonymized_telemetry=False,
        )
    )

    collection = get_collection_with_embedding(client, name=args.collection)

    query_embeddings = embed_texts(openai_client, [query])
    result = collection.query(query_embeddings=query_embeddings, n_results=max(1, args.limit))

    print(f"Query: {query}")
    ids = result.get("ids", [[]])[0]
    distances = result.get("distances", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    for rank, (card_id, dist, meta) in enumerate(
        zip(ids, distances, metadatas, strict=False), start=1
    ):
        name = meta.get("name", "unknown") if isinstance(meta, dict) else "unknown"
        print(f"{rank}. id={card_id} name={name} distance={dist}")


if __name__ == "__main__":
    main()
