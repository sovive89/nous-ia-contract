"""Deterministic, allowlisted mapping executor. No eval, expressions or arbitrary code."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from jsonschema import Draft202012Validator

class ExecutionError(ValueError):
    pass

def _segments(path: str) -> list[str]:
    if not isinstance(path, str) or not path or path.startswith("."):
        raise ExecutionError("invalid field path")
    parts = path.split(".")
    if len(parts) > 16 or any(not p or p in {"__proto__", "__class__", "__dict__"} for p in parts):
        raise ExecutionError("unsafe field path")
    return parts

def _get(data: dict[str, Any], path: str) -> Any:
    node: Any = data
    for part in _segments(path):
        if not isinstance(node, dict) or part not in node:
            raise ExecutionError(f"missing source path: {path}")
        node = node[part]
    return node

def _set(data: dict[str, Any], path: str, value: Any) -> None:
    node = data
    parts = _segments(path)
    for part in parts[:-1]:
        if part not in node:
            node[part] = {}
        if not isinstance(node[part], dict):
            raise ExecutionError("destination path collision")
        node = node[part]
    if parts[-1] in node:
        raise ExecutionError("duplicate destination path")
    node[parts[-1]] = deepcopy(value)

def execute_mapping(definition: dict[str, Any], payload: dict[str, Any],
                    *, approved: bool = False) -> dict[str, Any]:
    """Caller must verify active approved contract version using trusted registry.

    approved=True is a service-level authorization assertion, NOT an API parameter.
    """
    if not approved:
        raise ExecutionError("approved active version required")
    if not isinstance(payload, dict):
        raise ExecutionError("payload must be an object")
    mappings = definition.get("mappings")
    if not isinstance(mappings, list) or not mappings or len(mappings) > 500:
        raise ExecutionError("invalid mappings")
    result: dict[str, Any] = {}
    for item in mappings:
        if not isinstance(item, dict) or set(item) != {"source", "target"}:
            raise ExecutionError("only direct source/target mappings are supported")
        _set(result, item["target"], _get(payload, item["source"]))
    schema = definition.get("schema")
    if schema is not None:
        Draft202012Validator.check_schema(schema)
        errors = list(Draft202012Validator(schema).iter_errors(result))
        if errors:
            raise ExecutionError("mapped output violates destination schema")
    return result
