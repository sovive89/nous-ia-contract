import hashlib
import json

from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.persistence import Base, Contract, ContractVersion, Tenant, AuditEvent


def test_contract_persists_and_is_tenant_scoped(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'contracts.db'}")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with Session(engine) as session:
        t1, t2 = Tenant(slug="a"), Tenant(slug="b")
        session.add_all([t1, t2])
        session.flush()
        contract = Contract(tenant_id=t1.id, key="orders", source_system="pop9", destination_system="delivery")
        session.add(contract)
        session.flush()
        definition = {"fields": {"vl_total": "total_amount"}}
        digest = hashlib.sha256(json.dumps(definition, sort_keys=True).encode()).hexdigest()
        session.add(ContractVersion(tenant_id=t1.id, contract_id=contract.id, version=1,
                                    definition_json=definition, definition_hash=digest, created_by="tester"))
        session.add(AuditEvent(tenant_id=t1.id, actor_id="tester", action="created",
                               resource_type="contract", resource_id=contract.id))
        session.commit()
        tenant_a_id, tenant_b_id = t1.id, t2.id

    with Session(engine) as session:
        assert len(session.scalars(select(Contract).where(Contract.tenant_id == tenant_a_id)).all()) == 1
        assert len(session.scalars(select(Contract).where(Contract.tenant_id == tenant_b_id)).all()) == 0
        assert session.scalar(select(ContractVersion)).definition_json["fields"]["vl_total"] == "total_amount"
        assert session.scalar(select(AuditEvent)).action == "created"
    engine.dispose()
