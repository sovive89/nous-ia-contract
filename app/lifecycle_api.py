"""Local/test-only lifecycle API. Never expose without real identity middleware."""
import os
from contextlib import contextmanager
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.persistence import make_engine, make_session_factory, Contract, ContractVersion, AuditEvent
from app.contract_service import ContractService, LifecycleError

router = APIRouter(prefix="/v1/contracts", tags=["lifecycle"])

class NewContract(BaseModel):
    key: str = Field(min_length=1, max_length=128)
    source_system: str = Field(min_length=1, max_length=128)
    destination_system: str = Field(min_length=1, max_length=128)

class NewVersion(BaseModel):
    definition: dict

class Decision(BaseModel):
    reason: str | None = Field(default=None, max_length=2048)

class Activation(BaseModel):
    environment: str = Field(min_length=1, max_length=64)

def session_for(tenant, actor):
    # Header identity is for isolated local testing ONLY, not authentication.
    if os.getenv("NOUS_LIFECYCLE_MODE") != "local":
        raise HTTPException(503, "Lifecycle disabled pending authentication")
    url = os.getenv("DATABASE_URL", "")
    if not (url.startswith("sqlite:") or ("localhost" in url or "127.0.0.1" in url)):
        raise HTTPException(503, "Local mode requires a local database")
    if not tenant or not actor:
        raise HTTPException(401, "Local tenant and actor headers required")
    engine = make_engine(url)
    return engine, make_session_factory(engine)

def run(tenant, actor, callback):
    engine, factory = session_for(tenant, actor)
    try:
        with factory() as db:
            service = ContractService(db, tenant, actor)
            try:
                return callback(service, db)
            except (LifecycleError, IntegrityError, ValueError) as exc:
                db.rollback()
                raise HTTPException(409, str(exc)) from exc
    finally:
        engine.dispose()

@router.post("", status_code=201)
def create_contract(req: NewContract, x_local_tenant: str = Header(""), x_local_actor: str = Header("")):
    def op(s, db):
        c = s.create(req.key, req.source_system, req.destination_system)
        return {"id": c.id, "key": c.key}
    return run(x_local_tenant, x_local_actor, op)

@router.get("")
def list_contracts(x_local_tenant: str = Header(""), x_local_actor: str = Header("")):
    return run(x_local_tenant, x_local_actor, lambda s, db: [
        {"id": c.id, "key": c.key, "source_system": c.source_system, "destination_system": c.destination_system}
        for c in db.scalars(select(Contract).where(Contract.tenant_id == s.tenant_id)).all()])

@router.post("/{contract_id}/versions", status_code=201)
def create_version(contract_id: str, req: NewVersion, x_local_tenant: str = Header(""), x_local_actor: str = Header("")):
    return run(x_local_tenant, x_local_actor, lambda s, db: _version_result(s.create_version(contract_id, req.definition)))

def _version_result(v):
    return {"id": v.id, "contract_id": v.contract_id, "version": v.version, "status": v.status, "definition_hash": v.definition_hash}

@router.post("/{contract_id}/versions/{version_id}/submit")
def submit(contract_id: str, version_id: str, x_local_tenant: str = Header(""), x_local_actor: str = Header("")):
    return run(x_local_tenant, x_local_actor, lambda s, db: _version_result(s.submit(contract_id, version_id)))

@router.post("/{contract_id}/versions/{version_id}/approve")
def approve(contract_id: str, version_id: str, req: Decision, x_local_tenant: str = Header(""), x_local_actor: str = Header("")):
    return run(x_local_tenant, x_local_actor, lambda s, db: _version_result(s.decide(contract_id, version_id, True, req.reason)))

@router.post("/{contract_id}/versions/{version_id}/reject")
def reject(contract_id: str, version_id: str, req: Decision, x_local_tenant: str = Header(""), x_local_actor: str = Header("")):
    return run(x_local_tenant, x_local_actor, lambda s, db: _version_result(s.decide(contract_id, version_id, False, req.reason)))

@router.post("/{contract_id}/versions/{version_id}/activate")
def activate(contract_id: str, version_id: str, req: Activation, x_local_tenant: str = Header(""), x_local_actor: str = Header("")):
    def op(s, db):
        a = s.activate(contract_id, version_id, req.environment)
        return {"id": a.id, "version_id": a.version_id, "environment": a.environment}
    return run(x_local_tenant, x_local_actor, op)

@router.get("/{contract_id}/history")
def history(contract_id: str, x_local_tenant: str = Header(""), x_local_actor: str = Header("")):
    def op(s, db):
        s.contract(contract_id)
        versions = db.scalars(select(ContractVersion).where(
            ContractVersion.tenant_id == s.tenant_id, ContractVersion.contract_id == contract_id
        ).order_by(ContractVersion.version)).all()
        return {"versions": [_version_result(v) for v in versions]}
    return run(x_local_tenant, x_local_actor, op)
