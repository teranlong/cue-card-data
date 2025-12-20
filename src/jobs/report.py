"""List Chroma collections with counts and metadata."""

from __future__ import annotations

import chromadb

from src.config.settings import settings
from utils.chroma_utils import report


def main() -> None:
    client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    report_text = report(client)
    print(report_text)


if __name__ == "__main__":
    main()
