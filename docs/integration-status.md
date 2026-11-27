# Integration status (2026-11-20)

Implemented: `DiscoveryPipeline` composes tenant-scoped `SemanticRetrieval`, JEV `DecisionProvider` and OpenAI `ReviewAgent`. Returns a review proposal only, never activates. `execute_mapping` provides deterministic direct field copying and destination JSON Schema validation; no arbitrary transforms or code evaluation.

These modules are **not yet wired** to the authenticated API, registry activation checks, audit persistence or background processing. `execute_mapping(approved=True)` is an internal trusted-caller assertion and MUST NOT be exposed to clients. Before any production execution, load active contract version by tenant, contract and environment from trusted persistence, verify approval/activation, and derive authorization server-side.

Remaining: actual JEV/OpenAI credentialed calls; reconcile SDK response formats; audit trails and request correlation; full pipeline API; production authentication and tenant isolation; idempotent event processing, retries and error handling; deployment and end-to-end tests. No tests executed per user request. Do not describe as complete or production ready.
