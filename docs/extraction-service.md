# ExtractionService — first implementation slice

This is the first implemented component of the future ingestion layer, before RAG.

- `extract_json_fields(payload)` extracts observed leaf paths and JSON types from example payloads.
- `extract_schema_fields(schema)` extracts declared local JSON Schema properties, descriptions, required flags and unresolved references.
- Both are deterministic Python functions, with no external calls or semantic inference.
- The JSON extractor samples array entries by index; it does not infer schemas from a single sample.
- JSON Schema `$ref`, `allOf`, `oneOf`, `anyOf`, arrays' `items`, OpenAPI endpoints, authentication and remote discovery are **not yet supported**.
- No production data should be ingested without redaction, authorization, and tenant boundaries.

Next: schema reference resolution, OpenAPI adapter, evidence provenance and RAG indexing. The existing v0.1 API is unchanged.
