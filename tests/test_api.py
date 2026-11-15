from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_mapping_requires_review():
    response = client.post("/v1/contracts/evaluate", json={
        "tenant_id": "demo", "source_field": "vl_total", "target_field": "total_amount",
        "source_type": "number", "target_type": "number"
    })
    assert response.status_code == 200
    assert response.json()["recommendation"] == "REVIEW"
    assert response.json()["published"] is False

def test_incompatible_units():
    data = {"tenant_id": "demo", "source_field": "price", "target_field": "price",
            "source_type": "number", "target_type": "number",
            "source_unit": "BRL", "target_unit": "USD"}
    assert client.post("/v1/contracts/evaluate", json=data).json()["recommendation"] == "REJECT"

def test_schema_validation():
    result = client.post("/v1/contracts/validate", json={
        "schema_definition": {"type": "object", "required": ["total"], "properties": {"total": {"type": "number"}}},
        "payload": {"total": "wrong"}
    }).json()
    assert result["valid"] is False

def test_missing_tenant():
    response = client.post("/v1/contracts/evaluate", json={
        "source_field": "a", "target_field": "b", "source_type": "string", "target_type": "string"
    })
    assert response.status_code == 422
