"""Tenant-scoped pgvector evidence storage and cosine retrieval.

Requires pgvector extension and migration sql/semantic_evidence.sql.
Use only trusted tenant identity; do not expose raw SQL identifiers from callers.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.orm import Session

VECTOR_DIMENSIONS = 384

def _tenant(value: str) -> str:
    return str(UUID(value))

def _vector(values: list[float]) -> str:
    if len(values) != VECTOR_DIMENSIONS or not all(math.isfinite(x) for x in values):
        raise ValueError(f"Embedding must have {VECTOR_DIMENSIONS} finite values")
    return "[" + ",".join(format(float(x), ".9g") for x in values) + "]"

@dataclass(frozen=True)
class Match:
    evidence_id: str
    system: str
    path: str
    text: str
    metadata: dict[str, Any]
    distance: float

class PgVectorEvidenceStore:
    def __init__(self, session: Session, tenant_id: str):
        self.db = session
        self.tenant_id = _tenant(tenant_id)

    def upsert(self, records: list[dict[str, Any]]) -> int:
        """Caller owns transaction. No commit is performed."""
        for r in records:
            embedding = _vector(r["embedding"])
            self.db.execute(text("""
                INSERT INTO semantic_evidence
                    (tenant_id, evidence_id, system_name, field_path, content, metadata_json, embedding)
                VALUES
                    (:tenant, :id, :system, :path, :content,
                     CAST(:metadata AS jsonb), CAST(:embedding AS vector))
                ON CONFLICT (tenant_id, evidence_id) DO UPDATE SET
                    system_name = EXCLUDED.system_name,
                    field_path = EXCLUDED.field_path,
                    content = EXCLUDED.content,
                    metadata_json = EXCLUDED.metadata_json,
                    embedding = EXCLUDED.embedding
            """), {
                "tenant": self.tenant_id, "id": r["id"], "system": r["system"],
                "path": r["path"], "content": r["text"],
                "metadata": __import__("json").dumps(r["metadata"]),
                "embedding": embedding,
            })
        return len(records)

    def search(self, query_vector: list[float], limit: int = 8,
               exclude_system: str | None = None) -> list[Match]:
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        rows = self.db.execute(text("""
            SELECT evidence_id, system_name, field_path, content, metadata_json,
                   embedding <=> CAST(:embedding AS vector) AS distance
            FROM semantic_evidence
            WHERE tenant_id = :tenant
              AND (:exclude_system IS NULL OR system_name <> :exclude_system)
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """), {
            "tenant": self.tenant_id, "embedding": _vector(query_vector),
            "exclude_system": exclude_system, "limit": limit,
        }).mappings()
        return [Match(r["evidence_id"], r["system_name"], r["field_path"],
                      r["content"], r["metadata_json"], float(r["distance"])) for r in rows]
