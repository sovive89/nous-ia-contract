"""Tenant-scoped contract lifecycle. Callers must authenticate before using this service."""
import hashlib
import json
from sqlalchemy import select
from sqlalchemy.orm import Session
from jsonschema import Draft202012Validator
from app.persistence import Contract, ContractVersion, ContractApproval, ContractActivation, AuditEvent, utcnow

class LifecycleError(ValueError):
    pass

def digest(definition):
    return hashlib.sha256(json.dumps(definition, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def audit(session, tenant_id, actor, action, kind, resource, details=None):
    session.add(AuditEvent(tenant_id=tenant_id, actor_id=actor, action=action,
                           resource_type=kind, resource_id=resource, details_json=details or {}))

class ContractService:
    def __init__(self, session: Session, tenant_id: str, actor: str):
        if not tenant_id or not actor:
            raise LifecycleError("Authenticated tenant and actor required")
        self.db, self.tenant_id, self.actor = session, tenant_id, actor

    def contract(self, contract_id, lock=False):
        stmt = select(Contract).where(Contract.id == contract_id, Contract.tenant_id == self.tenant_id)
        if lock:
            stmt = stmt.with_for_update()
        result = self.db.scalar(stmt)
        if result is None:
            raise LifecycleError("Contract not found")
        return result

    def version(self, contract_id, version_id, lock=False):
        stmt = select(ContractVersion).where(
            ContractVersion.id == version_id, ContractVersion.contract_id == contract_id,
            ContractVersion.tenant_id == self.tenant_id)
        if lock:
            stmt = stmt.with_for_update()
        result = self.db.scalar(stmt)
        if result is None:
            raise LifecycleError("Version not found")
        return result

    def create(self, key, source_system, destination_system):
        contract = Contract(tenant_id=self.tenant_id, key=key, source_system=source_system,
                            destination_system=destination_system)
        self.db.add(contract)
        self.db.flush()
        audit(self.db, self.tenant_id, self.actor, "contract.created", "contract", contract.id)
        self.db.commit()
        return contract

    def create_version(self, contract_id, definition):
        self.contract(contract_id, lock=True)
        if not isinstance(definition, dict):
            raise LifecycleError("Definition must be an object")
        schema = definition.get("schema")
        if schema is not None:
            Draft202012Validator.check_schema(schema)
        existing = self.db.scalars(select(ContractVersion.version).where(
            ContractVersion.tenant_id == self.tenant_id, ContractVersion.contract_id == contract_id)).all()
        version = ContractVersion(tenant_id=self.tenant_id, contract_id=contract_id,
                                  version=max(existing, default=0) + 1,
                                  definition_json=definition, definition_hash=digest(definition),
                                  created_by=self.actor)
        self.db.add(version)
        self.db.flush()
        audit(self.db, self.tenant_id, self.actor, "version.created", "contract_version", version.id)
        self.db.commit()
        return version

    def submit(self, contract_id, version_id):
        version = self.version(contract_id, version_id, lock=True)
        if version.status != "DRAFT":
            raise LifecycleError("Only drafts can be submitted")
        version.status = "IN_REVIEW"
        audit(self.db, self.tenant_id, self.actor, "version.submitted", "contract_version", version.id)
        self.db.commit()
        return version

    def decide(self, contract_id, version_id, approved, reason=None):
        version = self.version(contract_id, version_id, lock=True)
        if version.status != "IN_REVIEW":
            raise LifecycleError("Only submitted versions can be reviewed")
        if version.created_by == self.actor:
            raise LifecycleError("Creator cannot review their own version")
        version.status = "APPROVED" if approved else "REJECTED"
        self.db.add(ContractApproval(tenant_id=self.tenant_id, version_id=version.id,
                                     decision=version.status, reviewer_id=self.actor, reason=reason))
        audit(self.db, self.tenant_id, self.actor, "version.reviewed", "contract_version",
              version.id, {"decision": version.status})
        self.db.commit()
        return version

    def activate(self, contract_id, version_id, environment):
        self.contract(contract_id, lock=True)
        version = self.version(contract_id, version_id, lock=True)
        if version.status != "APPROVED":
            raise LifecycleError("Only approved versions can activate")
        if not environment or len(environment) > 64:
            raise LifecycleError("Invalid environment")
        current = self.db.scalar(select(ContractActivation).where(
            ContractActivation.tenant_id == self.tenant_id,
            ContractActivation.contract_id == contract_id,
            ContractActivation.environment == environment,
            ContractActivation.deactivated_at.is_(None)))
        if current is not None:
            current.deactivated_at = utcnow()
            self.db.flush()
        activation = ContractActivation(tenant_id=self.tenant_id, contract_id=contract_id,
                                        version_id=version_id, environment=environment,
                                        activated_by=self.actor)
        self.db.add(activation)
        self.db.flush()
        audit(self.db, self.tenant_id, self.actor, "version.activated", "contract_activation",
              activation.id, {"version_id": version_id, "environment": environment})
        self.db.commit()
        return activation
