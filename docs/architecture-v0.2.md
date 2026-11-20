# NØUS IA Contracts v0.2 — Persistence and Versioning

Status: architecture specification; implementation pending. Branch: `feat/contracts-v0.2-persistence`.

## Scope
Preserve `GET /health`, `POST /v1/contracts/evaluate`, and `POST /v1/contracts/validate`. Introduce PostgreSQL-backed contract definitions, immutable published versions, human approval, activation history, and audit trails. Do not treat heuristic mapping as trusted semantic matching.

## Components
- FastAPI routers: existing evaluation/validation and new contract lifecycle routes.
- ContractService: tenant-scoped authorization, version state machine, schema validation, transaction boundaries.
- Persistence: SQLAlchemy 2, Alembic, PostgreSQL, Docker Compose for local development.
- AuditService: append-only audit events in the same transaction as state changes.
- Future modules: deterministic Contract Executor; RAG/JEV discovery-time mapping. Neither is part of v0.2.

## Data model
- `tenants(id, slug, created_at)`
- `contracts(id, tenant_id, key, source_system, destination_system, created_at)`
- `contract_versions(id, tenant_id, contract_id, version, status, definition_json, definition_hash, created_by, created_at)`
- `contract_approvals(id, tenant_id, version_id, decision, reviewer_id, reason, decided_at)`
- `contract_activations(id, tenant_id, contract_id, version_id, environment, activated_by, activated_at, deactivated_at)`
- `audit_events(id, tenant_id, actor_id, action, resource_type, resource_id, details_json, created_at)`

Constraints: unique `(tenant_id, key)` on contracts and `(contract_id, version)` on versions; FK tenant consistency; one current activation per `(tenant_id, contract_id, environment)` using partial unique index on `deactivated_at IS NULL`. Atomic deactivation and activation in one transaction, with row lock on contract. Definitions of submitted/approved/active versions are immutable; corrections create a new version. Avoid mutating approved content even after deprecation.

## State machine
`DRAFT -> IN_REVIEW -> APPROVED -> ACTIVE -> DEPRECATED`. `IN_REVIEW -> REJECTED` is allowed; revisions create a fresh draft version. Approval is separate from activation. A contract can have v1 ACTIVE while v2 IN_REVIEW. Keep status and activation history consistent transactionally; activation is environment-specific, so effective active version must be resolved from activations rather than relying solely on version status.

## Security
Do not trust `tenant_id` from request JSON as authentication. Until an authenticated identity and tenant membership are implemented, restrict lifecycle mutations to local/test environment and do not deploy as multi-tenant production. All queries must be tenant-scoped; use PostgreSQL RLS as additional defense when identity binding is available. Audit approver identity; require approval by authorized reviewer.

## Proposed routes
- `POST /v1/contracts`
- `GET /v1/contracts`
- `POST /v1/contracts/{id}/versions`
- `POST /v1/contracts/{id}/versions/{version_id}/submit`
- `POST /v1/contracts/{id}/versions/{version_id}/approve`
- `POST /v1/contracts/{id}/versions/{version_id}/activate`
- `GET /v1/contracts/{id}/history`

## Acceptance criteria
1. Existing API tests continue to pass.
2. Create contract and two versions; validate definitions against JSON Schema.
3. Only approved version can activate; no in-place edits after submission.
4. One active version per contract/environment; rollback is an audited activation of an earlier approved version.
5. Restart service and retrieve contracts and full history.
6. Cross-tenant read/write tests fail; concurrent activation tests preserve uniqueness.
7. Local Docker Compose and Alembic migrations reproducible; no secrets committed.

## Implementation order
1. Docker Compose, dependencies, configuration and Alembic migration.
2. SQLAlchemy models/repositories, tenant-scoped service.
3. Lifecycle API and authorization boundary.
4. Integration, concurrency, audit and regression tests.
5. Executor and semantic mapping in later versions.
