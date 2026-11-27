"""Local-only execution endpoint; not production authentication."""
from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.lifecycle_api import run
from app.active_execution import execute_active_contract
from app.contract_executor import ExecutionError

router = APIRouter(prefix="/v1/contracts", tags=["execution"])

class ExecuteRequest(BaseModel):
    environment: str = Field(min_length=1, max_length=64)
    payload: dict[str, Any]

@router.post("/{contract_id}/execute")
def execute(contract_id: str, req: ExecuteRequest,
            x_local_tenant: str = Header(""), x_local_actor: str = Header("")):
    def op(service, db):
        try:
            result = execute_active_contract(
                db, tenant_id=service.tenant_id, actor=service.actor,
                contract_id=contract_id, environment=req.environment,
                payload=req.payload)
            db.commit()
            return result
        except ExecutionError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
    return run(x_local_tenant, x_local_actor, op)
