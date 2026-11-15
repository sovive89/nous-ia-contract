from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ifood_normalization():
    payload = {"tenant_id": "demo", "source": "ifood", "payload": {
        "eventId": "if-evt-1", "orderId": "if-001", "code": "PLACED",
        "total": "19.90", "currency": "BRL", "occurred_at": "2026-11-15T10:00:00Z"}}
    response = client.post("/v1/simulators/normalize", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["canonical_event"]["payload"]["total_minor"] == 1990
    assert result["persisted"] is False


def test_99food_normalization():
    payload = {"tenant_id": "demo", "source": "99food", "payload": {
        "event_id": "99-evt-1", "order_id": "99-001", "status": "CREATED",
        "amount": "19.90", "currency": "BRL", "occurred_at": "2026-11-15T10:00:00-03:00"}}
    response = client.post("/v1/simulators/normalize", json=payload)
    assert response.status_code == 200
    event = response.json()["canonical_event"]
    assert event["occurred_at"] == "2026-11-15T13:00:00Z"
    assert event["payload"]["total_minor"] == 1990


def test_invalid_amount_rejected():
    response = client.post("/v1/simulators/normalize", json={"tenant_id": "demo", "source": "99food", "payload": {
        "event_id": "x", "order_id": "y", "status": "CREATED", "amount": "1.999",
        "occurred_at": "2026-11-15T10:00:00Z"}})
    assert response.status_code == 422


def test_missing_id_rejected():
    response = client.post("/v1/simulators/normalize", json={"tenant_id": "demo", "source": "ifood", "payload": {
        "orderId": "x", "code": "PLACED", "total": "1.00",
        "occurred_at": "2026-11-15T10:00:00Z"}})
    assert response.status_code == 422
