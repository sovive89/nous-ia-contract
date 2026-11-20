import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.main import app
from app.persistence import Base, Tenant, ContractActivation, AuditEvent

def test_lifecycle_disabled_by_default(monkeypatch):
    monkeypatch.delenv("NOUS_LIFECYCLE_MODE", raising=False)
    assert TestClient(app).get("/v1/contracts").status_code == 503

def test_lifecycle_with_local_database(tmp_path, monkeypatch):
    dburl = "sqlite:///" + str(tmp_path / "contracts.sqlite")
    engine = create_engine(dburl)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        tenant = Tenant(slug="demo")
        db.add(tenant)
        db.commit()
        tenant_id = tenant.id
    monkeypatch.setenv("NOUS_LIFECYCLE_MODE", "local")
    monkeypatch.setenv("DATABASE_URL", dburl)
    client = TestClient(app)
    def headers(actor="author", tenant=tenant_id):
        return {"x-local-tenant": tenant, "x-local-actor": actor}
    created = client.post("/v1/contracts", headers=headers(), json={
        "key": "orders", "source_system": "pop9", "destination_system": "erp"})
    assert created.status_code == 201, created.text
    cid = created.json()["id"]
    assert client.get("/v1/contracts", headers=headers(tenant="unknown")).json() == []
    v = client.post(f"/v1/contracts/{cid}/versions", headers=headers(),
                    json={"definition": {"schema": {"type": "object"}}})
    assert v.status_code == 201, v.text
    vid = v.json()["id"]
    assert client.post(f"/v1/contracts/{cid}/versions/{vid}/submit", headers=headers()).status_code == 200
    assert client.post(f"/v1/contracts/{cid}/versions/{vid}/approve", headers=headers(),
                       json={}).status_code == 409
    assert client.post(f"/v1/contracts/{cid}/versions/{vid}/approve", headers=headers("reviewer"),
                       json={"reason": "checked"}).status_code == 200
    a = client.post(f"/v1/contracts/{cid}/versions/{vid}/activate",
                    headers=headers("reviewer"), json={"environment": "test"})
    assert a.status_code == 200, a.text
    assert len(client.get(f"/v1/contracts/{cid}/history", headers=headers()).json()["versions"]) == 1
    with Session(engine) as db:
        assert db.scalar(select(ContractActivation)).version_id == vid
        assert len(db.scalars(select(AuditEvent)).all()) >= 5
    engine.dispose()
