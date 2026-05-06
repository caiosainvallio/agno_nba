# Load DATABASE_URL, GROQ_API_KEY, etc. from `.env` when present.
set dotenv-load := true

PORT := "8000"

default:
    @just --list

# Install / sync Python dependencies (uv).
deps:
    uv sync

# Copy `.env.example` → `.env` if `.env` does not exist.
env-init:
    #!/usr/bin/env bash
    set -euo pipefail
    if [[ ! -f .env ]]; then
        cp .env.example .env
        echo "Created .env from .env.example — set GROQ_API_KEY and verify DATABASE_URL."
    else
        echo ".env already exists."
    fi

# Start Postgres + pgvector (`docker compose` works if docker aliases to podman).
db-up:
    docker compose up -d

db-down:
    docker compose down

db-logs:
    docker compose logs -f postgres

# API dev server (reload). Requires Postgres reachable and vars in `.env`.
dev:
    uv run uvicorn agno_nba.api:app --reload --host 0.0.0.0 --port {{PORT}}

# API without reload.
run:
    uv run uvicorn agno_nba.api:app --host 0.0.0.0 --port {{PORT}}

# Smoke: OpenAPI `/chat`; full agent call only if `GROQ_API_KEY` is set.
smoke:
    uv run python scripts/smoke_chat.py

# First-time setup: env file template, deps, database container.
bootstrap: env-init deps db-up
    @echo "Next: edit .env (GROQ_API_KEY), wait for Postgres healthy, then: just dev"
