"""Extractor -> retrieval-ready semantic evidence, with pluggable embeddings.

This module does not call a remote model or claim to provide a trained RAG.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Protocol

from app.extraction import extract_json_fields, extract_schema_fields


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    system: str
    path: str
    field_type: str
    text: str
    metadata: dict[str, Any]


def build_evidence(
    system: str,
    *,
    schema: dict[str, Any] | None = None,
    payload: Any = None,
    has_payload: bool = False,
) -> list[Evidence]:
    """Build stable evidence records; caller supplies only authorized, sanitized inputs."""
    if not system.strip():
        raise ValueError("system is required")
    if schema is None and not has_payload:
        raise ValueError("schema or payload required")
    records: list[Evidence] = []
    if schema is not None:
        for field in extract_schema_fields(schema):
            records.append(_record(system, field, "schema"))
    if has_payload:
        for field in extract_json_fields(payload):
            records.append(_record(system, field, "payload"))
    return records


def _record(system: str, field: dict[str, Any], source: str) -> Evidence:
    path = str(field["path"])
    typ = str(field["type"])
    description = field.get("description") or ""
    # Never include raw payload values in retrieval evidence.
    text = f"system: {system}; path: {path}; type: {typ}; description: {description}"
    key = json.dumps([system, source, path, typ, description], ensure_ascii=False)
    identifier = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return Evidence(identifier, system, path, typ, text, {
        "source": source,
        "required": field.get("required"),
        "reference": field.get("reference"),
    })


def embed_evidence(records: list[Evidence], provider: EmbeddingProvider) -> list[dict[str, Any]]:
    """Produce vector records for a storage adapter; does not persist them."""
    vectors = provider.embed([r.text for r in records]) if records else []
    if len(vectors) != len(records):
        raise ValueError("embedding provider returned wrong vector count")
    if vectors and (not vectors[0] or any(len(v) != len(vectors[0]) for v in vectors)):
        raise ValueError("inconsistent embedding dimensions")
    return [{
        "id": record.evidence_id,
        "system": record.system,
        "path": record.path,
        "text": record.text,
        "metadata": record.metadata,
        "embedding": vector,
    } for record, vector in zip(records, vectors)]
