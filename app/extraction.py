"""Deterministic extraction of structural evidence; no semantic inference."""
from __future__ import annotations

from typing import Any


def extract_json_fields(payload: Any) -> list[dict[str, Any]]:
    """Return leaf fields with JSON Pointer paths and observed types."""
    fields: list[dict[str, Any]] = []

    def json_type(value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "number"
        if isinstance(value, str):
            return "string"
        if isinstance(value, list):
            return "array"
        return "object"

    def escape(part: str) -> str:
        return part.replace("~", "~0").replace("/", "~1")

    def visit(value: Any, path: str) -> None:
        if isinstance(value, dict):
            if not value:
                fields.append({"path": path or "/", "type": "object"})
            for key, child in value.items():
                visit(child, path + "/" + escape(str(key)))
        elif isinstance(value, list):
            if not value:
                fields.append({"path": path or "/", "type": "array"})
            else:
                # Sample array elements without inferring a fixed array length.
                for index, child in enumerate(value):
                    visit(child, path + "/" + str(index))
        else:
            fields.append({"path": path or "/", "type": json_type(value)})

    visit(payload, "")
    return fields


def extract_schema_fields(schema: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract local JSON Schema property declarations, without resolving $ref."""
    fields: list[dict[str, Any]] = []

    def escape(part: str) -> str:
        return part.replace("~", "~0").replace("/", "~1")

    def visit(node: dict[str, Any], path: str, required: bool = False) -> None:
        props = node.get("properties", {})
        if not isinstance(props, dict):
            return
        required_names = node.get("required", [])
        if not isinstance(required_names, list):
            required_names = []
        for name, definition in props.items():
            if not isinstance(definition, dict):
                continue
            child_path = path + "/" + escape(str(name))
            fields.append({
                "path": child_path,
                "type": definition.get("type", "unspecified"),
                "description": definition.get("description"),
                "required": name in required_names,
                "reference": definition.get("$ref"),
            })
            visit(definition, child_path, name in required_names)

    visit(schema, "")
    return fields
