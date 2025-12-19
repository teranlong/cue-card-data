"""Delete a Chroma collection by name (or remove all)."""

from __future__ import annotations

import argparse

import chromadb
from src.config.settings import settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delete a Chroma collection.")
    parser.add_argument(
        "collection",
        nargs="?",
        help="Name of the collection to delete.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Delete all collections.",
    )
    args = parser.parse_args()
    if not args.all and not args.collection:
        parser.error("Please provide a collection name or use --all.")
    return args


def main() -> None:
    args = parse_args()
    client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)

    if args.all:
        collections = client.list_collections()
        if not collections:
            print("No collections to delete.")
            return
        for col in collections:
            try:
                client.delete_collection(name=col.name)
                print(f"Deleted collection '{col.name}'.")
            except Exception as exc:  # noqa: BLE001
                print(f"Failed to delete collection '{col.name}': {exc}")
        return

    try:
        client.delete_collection(name=args.collection)
        print(f"Deleted collection '{args.collection}'.")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to delete collection '{args.collection}': {exc}")


if __name__ == "__main__":
    main()
