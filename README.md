# cue-card-data

Chroma-backed vector store for card data (TSV) plus a handful of maintenance jobs.

## Requirements
- Python 3.11+ with `uv` (`pip install uv`)
- Docker Desktop (for Chroma)
- An OpenAI API key (.env)

## Setup
1) Copy `.env.example` to `.env` and set `OPENAI_API_KEY`. Adjust `CHROMA_PORT` if 8000 is taken.  
2) Install dependencies: `uv sync`

## Services
- Start Chroma: `make start` (uses `docker/docker-compose.yml`)  
- Stop Chroma: `make stop`

## Collections
- Collections are defined in `chroma.config.json` under the top-level `chroma.collections` array.
- Create/refresh from config: `make create_collections` (add `ARGS="--rebuild"` to drop/recreate first, or `ARGS="--config path/to/file.json"` to point at a different config).
- Example `chroma.config.json` entry:

```json
{
  "chroma": {
    "collections": [
      {
        "source_path": "data/source/cards_v1.tsv",
        "provider": "openai",
        "embedding_model": "text-embedding-3-small",
        "variant": "v1",
        "batch_size": 200
      }
    ]
  }
}
```
- Remove a collection: `make remove ARGS="<collection-name>"`  
  Remove all collections: `make remove ARGS="--all"`

## Reporting & queries
- Count check vs TSV: `make report` (defaults to the first collection in `chroma.config.json`; override with `ARGS="--collection <name> --source <tsv>"`)  
- Query a collection: `make query QUERY="search text"` (defaults to the first collection in `chroma.config.json`; override with `COLLECTION=<name>`)

## Linting
- `make lint` (runs `ruff` and `mypy` via `uv run`)

## Notes
- Jobs can also be run directly, e.g. `uv run python -m src.jobs.create_chroma_collections`.
- Default collection/model settings live in `chroma.config.json`; service host/port live in `src/config/settings.py`.
