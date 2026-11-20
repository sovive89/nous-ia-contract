"""Structured decision boundary for RAG candidate evaluation.

No model is trusted to approve contracts. JEV is optional and fail-closed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class Decision:
    candidate_id: str | None
    risk_score: float | None
    equivalence_probability: float | None
    provider: str
    requires_review: bool = True


class DecisionProvider(Protocol):
    def evaluate(self, source: dict[str, Any], candidates: list[dict[str, Any]]) -> Decision: ...


class JEVDecisionProvider:
    """SDK adapter; accepts an injected, explicitly configured JEV client.

    The SDK method and response schema must be verified before enabling.
    """

    def __init__(self, client: Any):
        self.client = client

    def evaluate(self, source: dict[str, Any], candidates: list[dict[str, Any]]) -> Decision:
        if not candidates:
            return Decision(None, None, None, "jev", True)
        ids = [str(c["evidence_id"]) for c in candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate candidate ids")
        if not hasattr(self.client, "system_one"):
            raise RuntimeError("JEV client does not expose verified system_one interface")

        # API contract deliberately isolated here; verify Choice/Score/Noul
        # request/response types against the installed SDK before enabling.
        raise NotImplementedError(
            "JEV SDK request/response mapping is not verified; fail closed"
        )


def build_decision_input(source: dict[str, Any], matches: list[Any]) -> list[dict[str, Any]]:
    """Only include retrieval evidence; no raw payload values or cross-tenant data."""
    return [
        {"evidence_id": str(m.evidence_id), "system": m.system,
         "path": m.path, "description": m.text, "distance": float(m.distance)}
        for m in matches
    ]
