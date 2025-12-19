ROOT_DIR := $(CURDIR)

# Defaults for convenience when calling: make query <collection> <text>
COLLECTION ?= $(word 2,$(MAKECMDGOALS))
QUERY ?= $(wordlist 3,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))

.PHONY: start stop report reset install lint create_collections remove query

start:
	powershell -NoProfile -ExecutionPolicy Bypass -File "$(ROOT_DIR)/scripts/start_services.ps1" $(ARGS)

stop:
	powershell -NoProfile -ExecutionPolicy Bypass -File "$(ROOT_DIR)/scripts/stop_services.ps1" $(ARGS)

report:
	uv run python -m src.jobs.report $(ARGS)

install:
	uv sync

lint:
	uv run ruff check src
	uv run mypy src

create_collections:
	uv run python -m src.jobs.create_chroma_collections $(ARGS)

remove:
	uv run python -m src.jobs.remove_collection $(ARGS)

query:
	uv run python scripts/query_cards.py --collection "$(COLLECTION)" "$(QUERY)"
