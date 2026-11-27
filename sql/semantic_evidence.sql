-- Run AFTER the existing tenant table has been migrated.
-- Requires PostgreSQL with pgvector installed on the server.
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS semantic_evidence (
    tenant_id varchar(36) NOT NULL REFERENCES tenants(id),
    evidence_id varchar(64) NOT NULL,
    system_name varchar(128) NOT NULL,
    field_path text NOT NULL,
    content text NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    embedding vector(384) NOT NULL,
    indexed_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, evidence_id)
);
CREATE INDEX IF NOT EXISTS ix_semantic_evidence_tenant_system
    ON semantic_evidence (tenant_id, system_name);
-- HNSW approximate nearest neighbor index; add only when scale justifies it.
-- Exact tenant-filtered cosine search is used initially for correctness.
ALTER TABLE semantic_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE semantic_evidence FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS semantic_evidence_tenant_scope ON semantic_evidence;
CREATE POLICY semantic_evidence_tenant_scope ON semantic_evidence
    USING (tenant_id = current_setting('app.tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true));
-- Use a non-owner DB role with least privilege. Table owners and privileged
-- roles can bypass RLS. Set app.tenant_id via SET LOCAL within each transaction.
