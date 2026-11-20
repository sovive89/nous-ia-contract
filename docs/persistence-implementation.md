# NØUS IA Contracts — Persistence foundation

Implemented in branch feat/contracts-v0.2-persistence: SQLAlchemy 2 entities, initial Alembic migration, local PostgreSQL 16 Docker Compose, and metadata smoke test.

## Setup (not yet run in a deployment)
Set POSTGRES_PASSWORD in a local .env (never commit). Run docker compose up -d. Set DATABASE_URL=postgresql+psycopg://nous:<password>@localhost:5432/nous_contracts. Install dependencies, then run alembic upgrade head and pytest -q.

## Security and scope
This is a persistence foundation, **not a production-ready contract service**. There are no lifecycle API routes, authorization, RLS, immutable-version enforcement, or append-only audit enforcement yet. These must be implemented and tested before accepting real multi-tenant traffic. Migration currently uses metadata.create_all and should be replaced by explicit Alembic operations before production schema evolution. The partial unique index for current activations is PostgreSQL-specific.

RAG, JEV, ML and the deterministic executor are not integrated. Existing API remains unchanged.
