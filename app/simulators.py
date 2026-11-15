"""Offline, synthetic marketplace-to-PDV adapters. Not official API contracts."""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/simulators", tags=["Simulators"])


class SimulationRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    source: Literal["ifood", "99food"]
    payload: dict[str, Any]


def money_minor(value: Any) -> int:
    """Parse a decimal string or integer major-unit amount without float rounding."""
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError("amount must be a decimal string or integer")
    try:
        amount = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("invalid amount") from exc
    if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
        raise ValueError("amount must be nonnegative with at most two decimals")
    return int(amount * 100)


def required_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a nonempty string")
    return value


def normalize(tenant_id: str, source: str, payload: dict[str, Any]) -> dict[str, Any]:
    if source == "ifood":
        # Synthetic iFood-inspired format; NOT a verified iFood webhook.
        order_id = required_str(payload, "orderId")
        event_id = required_str(payload, "eventId")
        status = required_str(payload, "code")
        amount = money_minor(payload.get("total"))
        currency = payload.get("currency", "BRL")
    elif source == "99food":
        # Synthetic 99Food-inspired format; NOT a verified 99Food webhook.
        order_id = required_str(payload, "order_id")
        event_id = required_str(payload, "event_id")
        status = required_str(payload, "status")
        amount = money_minor(payload.get("amount"))
        currency = payload.get("currency", "BRL")
    else:
        raise ValueError("unsupported source")
    if currency != "BRL":
        raise ValueError("only BRL is supported by the simulator")
    if not isinstance(payload.get("occurred_at"), str):
        raise ValueError("occurred_at must be an ISO 8601 string")
    try:
        timestamp = datetime.fromisoformat(payload["occurred_at"].replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            raise ValueError()
    except ValueError as exc:
        raise ValueError("occurred_at must include a timezone") from exc
    return {
        "tenant_id": tenant_id,
        "source": source,
        "event_id": event_id,
        "event_type": "order.status_changed",
        "schema_ref": "nous.order-status.v1",
        "occurred_at": timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "subject": {"entity_type": "order", "external_id": order_id},
        "payload": {
            "order_id": order_id,
            "source_status": status,
            "total_minor": amount,
            "currency": currency,
        },
        "simulation": True,
    }


@router.post("/normalize")
def simulate(req: SimulationRequest):
    try:
        canonical = normalize(req.tenant_id, req.source, req.payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "canonical_event": canonical,
        "requires_human_review": True,
        "persisted": False,
        "published": False,
        "warning": "Synthetic simulation only; no official provider integration or durable idempotency.",
    }
