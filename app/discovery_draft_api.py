"""Local-only conversion of a reviewed discovery into a draft contract version.

The caller must reference a persisted discovery audit event belonging to its tenant.
No model recommendation automatically submits, approves or activates a contract.
"""
from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from app.lifecycle_api import run
from app.persistence import AuditEvent
from app.contract_service import audit

router = APIRouter(prefix="/v1/discovery", tags=["discovery"])

class DraftRequest(BaseModel):
    contract_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)

@router.post("/draft", status_code=201)
def create_draft(req: DraftRequest, x_local_tenant: str = Header(""),
                 x_local_actor: str = Header("")):
    def op(service, db):
        try:
            UUID(req.request_id)
        except ValueError as exc:
            raise HTTPException(422, "invalid discovery ID") from exc
        service.contract(req.contract_id)
        event = db.scalar(select(AuditEvent).where(
            AuditEvent.tenant_id == service.tenant_id,
            AuditEvent.id == req.request_id,
            AuditEvent.action == "discovery.evaluated"))
        # Discovery request_id is the audit resource_id, not its row primary key.
        if event is None:
            event = db.scalar(select(AuditEvent).where(
                AuditEvent.tenant_id == service.tenant_id,
                AuditEvent.resource_id == req.request_id,
                AuditEvent.action == "discovery.evaluated"))
        if event is None:
            raise HTTPException(404, "discovery not found")
        details = event.details_json
        decision = details.get("decision") or {}
        candidate_id = decision.get("candidate_id")
        if not candidate_id or candidate_id not in details.get("candidate_ids", []):
            raise HTTPException(409, "discovery has no valid candidate")
        if (details.get("review") or {}).get("verdict") == "reject_recommended":
            raise HTTPException(409, "reviewer recommended rejection")
        # Explicit mapping paths are deliberately not inferred from an evidence ID.
        # User must supply verified source/target mapping in a separate version definition.
        return {"contract_id": req.contract_id, "discovery_id": req.request_id,
                "candidate_id": candidate_id, "status": "awaiting_mapping_confirmation",
                "created": False, "requires_human_review": True}
    return run(x_local_tenant, x_local_actor, op)
