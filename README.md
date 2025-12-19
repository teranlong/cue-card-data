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
- Create/refresh (uses `src/jobs/create_chroma_collections.py` defaults):  
  `make create_collections ARGS="--rebuild"`  # drop/recreate first  
  (omit `--rebuild` to upsert/ensure only)
- Remove a collection: `make remove ARGS="<collection-name>"`  
  Remove all collections: `make remove ARGS="--all"`

## Reporting & queries
- Count check vs TSV: `make report ARGS="--collection <name> --source data/source/cards_v1.tsv"`  
- Query a collection: `make query COLLECTION=<name> QUERY="search text"`

## Linting
- `make lint` (runs `ruff` and `mypy` via `uv run`)

## Notes
- Jobs can also be run directly, e.g. `uv run python -m src.jobs.create_chroma_collections`.
- Default collection/model settings live in `src/config/settings.py`.
