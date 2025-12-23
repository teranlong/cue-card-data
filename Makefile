ROOT_DIR := $(CURDIR)
export POSTGRES_PORT ?= 56432

$(eval $(RAW_ARGS):;@:)

.PHONY: start stop start-postgres start-all stop-postgres stop-all postgres-rebuild report reset install lint create_collections remove remove_all query

start:
	powershell -NoProfile -ExecutionPolicy Bypass -File "$(ROOT_DIR)/scripts/start_services.ps1" $(ARGS)

start-postgres:
	powershell -NoProfile -ExecutionPolicy Bypass -File "$(ROOT_DIR)/scripts/start_services.ps1" -Services card-data-postgres-001 $(ARGS)

start-all:
	powershell -NoProfile -ExecutionPolicy Bypass -File "$(ROOT_DIR)/scripts/start_services.ps1" -Services card-data-chroma-001 card-data-postgres-001 $(ARGS)

stop:
	powershell -NoProfile -ExecutionPolicy Bypass -File "$(ROOT_DIR)/scripts/stop_services.ps1" $(ARGS)

stop-postgres:
	powershell -NoProfile -ExecutionPolicy Bypass -File "$(ROOT_DIR)/scripts/stop_services.ps1" -Services card-data-postgres-001 $(ARGS)

stop-all:
	powershell -NoProfile -ExecutionPolicy Bypass -File "$(ROOT_DIR)/scripts/stop_services.ps1" -Services card-data-chroma-001 card-data-postgres-001 $(ARGS)

postgres-rebuild:
	docker compose -f "$(ROOT_DIR)/docker/docker-compose.yml" down card-data-postgres-001 --volumes
	docker compose -f "$(ROOT_DIR)/docker/docker-compose.yml" up -d --build card-data-postgres-001

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
