"""Offline discovery-time indexing and retrieval. Not used per operational event."""
from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session
from app.semantic_evidence import build_evidence, embed_evidence, EmbeddingProvider
from app.vector_store import PgVectorEvidenceStore, Match

class SemanticRetrieval:
    def __init__(self, session: Session, tenant_id: str, embeddings: EmbeddingProvider):
        self.store = PgVectorEvidenceStore(session, tenant_id)
        self.embeddings = embeddings

    def index_schema(self, system: str, schema: dict[str, Any]) -> int:
        records = build_evidence(system, schema=schema)
        return self.store.upsert(embed_evidence(records, self.embeddings))

    def find_candidates(self, system: str, path: str, field_type: str,
                        description: str = "", limit: int = 8) -> list[Match]:
        query = f"system: {system}; path: {path}; type: {field_type}; description: {description}"
        vector = self.embeddings.embed([query])[0]
        return self.store.search(vector, limit=limit, exclude_system=system)
