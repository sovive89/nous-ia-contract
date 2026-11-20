# NØUS IA Contracts — semantic retrieval foundation

This is the discovery-time RAG retrieval layer, not a complete RAG/decision system.

## Flow
Python Extractor -> semantic evidence -> EmbeddingProvider -> pgvector -> tenant-scoped candidate retrieval -> (future) JEV/ML -> human review -> immutable contract.

Run sql/semantic_evidence.sql after the core tenant migration on a PostgreSQL instance with pgvector available. Use a local pre-downloaded 384-dimension sentence-transformers model (install sentence-transformers separately). Set up a least-privilege database role and transaction-local app.tenant_id before indexing or querying; the Python store also filters tenant_id in SQL.

Use a single fixed embedding model per index. If the model changes, rebuild the index. Never index sensitive payload values or credentials. Schema descriptions may also contain secrets or sensitive information and must be sanitized upstream. This layer indexes schemas, not runtime events.

## Current limitations
No production authorization integration, no automatic schema discovery, no background indexing worker, no JEV connector, no ranking calibration, no vector migration integrated into Alembic, and no tests executed. This code must not be exposed to production workloads.
