"""Validate collection document counts in Chroma."""

from __future__ import annotations

import argparse

import chromadb
import pandas as pd
from src.config.settings import settings
from src.utils.chroma import get_collection_with_embedding


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate collection counts.")
    parser.add_argument(
        "--collection",
        default=settings.default_collection_name,
        help="Collection name to compare with the source (defaults to the configured default).",
    )
    parser.add_argument(
        "--source",
        default=settings.card_source_path,
        help="Path to cards TSV file to compare.",
    )
    return parser.parse_args()


def expected_count(path: str) -> int:
    df = pd.read_csv(path, sep="\t", dtype=str)
    return len(df.index)


def main() -> None:
    args = parse_args()
    client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)

    collections = client.list_collections()
    if not collections:
        print("No collections found.")
        return

    rows = []
    for col in collections:
        coll = get_collection_with_embedding(client, name=col.name)
        rows.append(
            {
                "name": col.name,
                "count": coll.count(),
                "metadata": col.metadata or {},
            }
        )

    df = pd.DataFrame(rows)
    print("Collections overview:")
    print(df.to_string(index=False))

    # Keep the original source-vs-collection comparison for the target collection.
    selected = next((r for r in rows if r["name"] == args.collection), None)
    if selected is None:
        print(f"Collection '{args.collection}' not found; skipping source comparison.")
        return

    chroma_count = selected["count"]
    source_rows = expected_count(args.source)

    print(f"Collection '{args.collection}' count: {chroma_count}")
    print(f"Source rows: {source_rows}")

    if chroma_count == source_rows:
        print("Counts match.")
    else:
        print("Counts differ. Re-run ingestion or inspect data.")


if __name__ == "__main__":
    main()
