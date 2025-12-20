ROOT_DIR := $(CURDIR)

# Query variables (set these explicitly: make query QUERY="text" [COLLECTION=name])
COLLECTION ?=
QUERY ?=

RAW_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
FIRST_ARG := $(firstword $(RAW_ARGS))
SECOND_ARG := $(word 2,$(RAW_ARGS))

USER_COLLECTION := $(strip $(if $(COLLECTION),$(COLLECTION),$(if $(SECOND_ARG),$(FIRST_ARG))))
USER_QUERY := $(strip $(if $(QUERY),$(QUERY),$(if $(SECOND_ARG),$(SECOND_ARG),$(FIRST_ARG))))

$(eval $(RAW_ARGS):;@:)

.PHONY: start stop report reset install lint create_collections remove remove_all query

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

remove_all:
	uv run python -m src.jobs.remove_collection --all

query:
	uv run python -m scripts.query_cards $(if $(strip $(USER_COLLECTION)),--collection "$(strip $(USER_COLLECTION))") "$(USER_QUERY)"
