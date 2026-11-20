from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Literal
from jsonschema import Draft202012Validator
from difflib import SequenceMatcher

app = FastAPI(title="NØUS IA Contract Intelligence", version="0.1.0")

class EvaluateRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    source_field: str = Field(min_length=1)
    target_field: str = Field(min_length=1)
    source_type: Literal["string", "number", "integer", "boolean", "object", "array"]
    target_type: Literal["string", "number", "integer", "boolean", "object", "array"]
    source_unit: str | None = None
    target_unit: str | None = None
    sample: Any = None

class SchemaRequest(BaseModel):
    schema_definition: dict[str, Any]
    payload: Any

@app.get("/health")
def health():
    return {"status": "ok", "service": "nous-ia-contract", "version": "0.1.0"}

@app.post("/v1/contracts/evaluate")
def evaluate(req: EvaluateRequest):
    type_compatible = req.source_type == req.target_type or (
        req.source_type == "integer" and req.target_type == "number"
    )
    unit_compatible = req.source_unit == req.target_unit or (
        req.source_unit is None and req.target_unit is None
    )
    similarity = round(SequenceMatcher(None, req.source_field.lower(), req.target_field.lower()).ratio(), 4)
    warnings = []
    if not type_compatible:
        warnings.append("TYPE_MISMATCH")
    if not unit_compatible:
        warnings.append("UNIT_MISMATCH")
    if similarity < 0.5:
        warnings.append("LOW_NAME_SIMILARITY")
    return {
        "tenant_id": req.tenant_id,
        "mapping": {"source": req.source_field, "target": req.target_field},
        "checks": {"type_compatible": type_compatible, "unit_compatible": unit_compatible, "name_similarity": similarity},
        "warnings": warnings,
        "recommendation": "REJECT" if not type_compatible or not unit_compatible else "REVIEW",
        "requires_human_review": True,
        "published": False,
        "engines": {"jev": "not_configured", "openai_rag": "not_configured", "python_ml": "not_trained", "mem0": "not_configured", "auditor_agent": "not_configured"}
    }

@app.post("/v1/contracts/validate")
def validate_schema(req: SchemaRequest):
    try:
        Draft202012Validator.check_schema(req.schema_definition)
        validator = Draft202012Validator(req.schema_definition)
        errors = sorted(validator.iter_errors(req.payload), key=lambda e: list(map(str, e.path)))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"valid": not errors, "errors": [{"path": list(e.path), "message": e.message} for e in errors]}

# Lifecycle endpoints remain disabled unless explicitly enabled for local tests.
from app.lifecycle_api import router as lifecycle_router
app.include_router(lifecycle_router)

# Execution is guarded by the same local-only lifecycle mode.
from app.execution_api import router as execution_router
app.include_router(execution_router)

# Local-only, provider-configured discovery pipeline.
from app.discovery_api import router as discovery_router
app.include_router(discovery_router)
