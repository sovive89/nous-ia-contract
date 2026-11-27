"""Resolve an active, approved version from trusted tenant-scoped persistence."""
from __future__ import annotations
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.persistence import Contract, ContractVersion, ContractActivation, ContractApproval, AuditEvent
from app.contract_executor import execute_mapping, ExecutionError

def execute_active_contract(session: Session, *, tenant_id: str, actor: str,
                            contract_id: str, environment: str,
                            payload: dict[str, Any]) -> dict[str, Any]:
    if not tenant_id or not actor or not environment:
        raise ExecutionError("trusted tenant, actor and environment required")
    contract = session.scalar(select(Contract).where(
        Contract.tenant_id == tenant_id, Contract.id == contract_id))
    if contract is None:
        raise ExecutionError("contract not found")
    activation = session.scalar(select(ContractActivation).where(
        ContractActivation.tenant_id == tenant_id,
        ContractActivation.contract_id == contract_id,
        ContractActivation.environment == environment,
        ContractActivation.deactivated_at.is_(None)))
    if activation is None:
        raise ExecutionError("no active contract in environment")
    version = session.scalar(select(ContractVersion).where(
        ContractVersion.tenant_id == tenant_id,
        ContractVersion.contract_id == contract_id,
        ContractVersion.id == activation.version_id,
        ContractVersion.status == "APPROVED"))
    if version is None:
        raise ExecutionError("active contract version is not approved")
    approval = session.scalar(select(ContractApproval).where(
        ContractApproval.tenant_id == tenant_id,
        ContractApproval.version_id == version.id,
        ContractApproval.decision == "APPROVED"))
    if approval is None:
        raise ExecutionError("missing human approval record")
    # Do not commit here; the caller owns the transaction.
    result = execute_mapping(version.definition_json, payload, approved=True)
    session.add(AuditEvent(
        tenant_id=tenant_id, actor_id=actor, action="contract.executed",
        resource_type="contract_version", resource_id=version.id,
        details_json={"contract_id": contract_id, "environment": environment,
                      "definition_hash": version.definition_hash,
                      "mapping_count": len(version.definition_json["mappings"])}))
    return {"contract_id": contract_id, "version_id": version.id,
            "definition_hash": version.definition_hash, "output": result}
