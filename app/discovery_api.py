"""Local-only discovery endpoint: tenant-scoped RAG -> JEV -> OpenAI.

Disabled outside NOUS_LIFECYCLE_MODE=local. Do not expose to public networks.
"""
from __future__ import annotations
import os
from uuid import uuid4
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.lifecycle_api import run
from app.persistence import AuditEvent
from app.retrieval_pipeline import SemanticRetrieval
from app.embedding_local import LocalEmbeddingProvider
from app.decision_provider import JEVDecisionProvider
from app.contract_review_agent import OpenAIContractReviewAgent
from app.discovery_pipeline import DiscoveryPipeline

router = APIRouter(prefix="/v1/discovery", tags=["discovery"])

class DiscoveryRequest(BaseModel):
    system: str = Field(min_length=1, max_length=128)
    path: str = Field(min_length=1, max_length=256)
    field_type: str = Field(min_length=1, max_length=64)
    description: str = Field(default="", max_length=1200)
    unit: str | None = Field(default=None, max_length=64)
    limit: int = Field(default=8, ge=1, le=20)

@router.post("/evaluate")
def evaluate(req: DiscoveryRequest, x_local_tenant: str = Header(""),
             x_local_actor: str = Header("")):
    # Never accept provider keys or tenant identity from request body.
    def op(service, db):
        model_path = os.getenv("NOUS_EMBEDDING_MODEL_PATH")
        if not model_path or not os.getenv("TYPESAFE_API_KEY") or not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(503, "Discovery providers not configured")
        from typesafe_sdk import TypeSafeClient
        from openai import OpenAI
        retrieval = SemanticRetrieval(db, service.tenant_id, LocalEmbeddingProvider(model_path))
        try:
            with TypeSafeClient() as jev:
                pipeline = DiscoveryPipeline(
                    retrieval, JEVDecisionProvider(jev),
                    OpenAIContractReviewAgent(OpenAI(timeout=30.0, max_retries=0)))
                result = pipeline.evaluate(**req.model_dump())
        except (ValueError, RuntimeError, KeyError, AttributeError, TypeError) as exc:
            db.rollback()
            # Do not disclose third-party error bodies or sensitive evidence.
            raise HTTPException(502, "Discovery evaluation failed") from exc
        request_id = str(uuid4())
        db.add(AuditEvent(
            tenant_id=service.tenant_id, actor_id=service.actor,
            action="discovery.evaluated", resource_type="discovery",
            resource_id=request_id,
            details_json={
                "source_system": req.system, "source_path": req.path,
                "candidate_ids": [c["evidence_id"] for c in result["candidates"]],
                "decision": result["decision"], "review": result["review"],
                "published": False,
            }))
        db.commit()
        return {"request_id": request_id, **result}
    return run(x_local_tenant, x_local_actor, op)
