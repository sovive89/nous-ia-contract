from app.extraction import extract_json_fields, extract_schema_fields


def test_json_extraction_preserves_types_and_paths():
    fields = extract_json_fields({"vl_total": 15.5, "ativo": True, "itens": [{"id": 3}]})
    assert {"path": "/vl_total", "type": "number"} in fields
    assert {"path": "/ativo", "type": "boolean"} in fields
    assert {"path": "/itens/0/id", "type": "integer"} in fields


def test_json_pointer_escaping():
    assert extract_json_fields({"a/b~c": None}) == [{"path": "/a~1b~0c", "type": "null"}]


def test_schema_extraction_required_and_description():
    schema = {"type": "object", "required": ["pedido"], "properties": {
        "pedido": {"type": "object", "description": "Pedido", "properties": {
            "valor": {"type": "number", "description": "Valor total"}
        }, "required": ["valor"]}
    }}
    fields = extract_schema_fields(schema)
    assert fields[0]["required"] is True
    assert fields[1]["path"] == "/pedido/valor"
    assert fields[1]["description"] == "Valor total"
    assert fields[1]["required"] is True
