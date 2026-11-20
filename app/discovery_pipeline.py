"""Discovery-time orchestration: tenant-scoped RAG -> JEV -> OpenAI reviewer.

No activation, persistence or external execution occurs here. Caller owns transaction.
"""
from __future__ import annotations
from dataclasses import asdict
from typing import Any
from app.decision_provider import DecisionProvider, build_decision_input
from app.contract_review_agent import ReviewAgent

class DiscoveryPipeline:
    def __init__(self, retrieval: Any, decision: DecisionProvider, reviewer: ReviewAgent):
        self.retrieval, self.decision, self.reviewer = retrieval, decision, reviewer

    def evaluate(self, *, system: str, path: str, field_type: str,
                 description: str = "", unit: str | None = None,
                 limit: int = 8) -> dict[str, Any]:
        if not 1 <= limit <= 20:
            raise ValueError("limit must be between 1 and 20")
        source = {"system": system, "path": path, "field_type": field_type,
                  "description": description, "unit": unit}
        matches = self.retrieval.find_candidates(system, path, field_type, description, limit)
        candidates = build_decision_input(source, matches)
        if not candidates:
            return {"status": "no_evidence", "source": source, "candidates": [],
                    "decision": None, "review": None, "requires_human_review": True,
                    "published": False}
        decision = self.decision.evaluate(source, candidates)
        if decision.candidate_id is not None and decision.candidate_id not in {
            c["evidence_id"] for c in candidates
        }:
            raise ValueError("decision selected unknown evidence")
        # A reviewer is independently prompted to challenge the decision.
        review = self.reviewer.review(source, asdict(decision), candidates)
        return {"status": "reviewed", "source": source, "candidates": candidates,
                "decision": asdict(decision), "review": review.model_dump(),
                "requires_human_review": True, "published": False}
