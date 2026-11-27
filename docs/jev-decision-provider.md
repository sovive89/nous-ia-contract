# JEV Decision Provider — integration boundary

The RAG retrieval pipeline supplies candidate evidence. The JEV provider is optional and cannot activate contracts.

## Data flow
1. Extract source fields without payload values.
2. Retrieve candidate evidence within the authenticated tenant.
3. Build decision input with candidate evidence IDs, paths, descriptions and vector distances.
4. Ask the decision provider to select one of the known IDs and assess risk/equivalence.
5. Reject unknown IDs, malformed scores, insufficient evidence or provider errors.
6. Run deterministic Contract Validator, then human approval and versioned Registry.

## Current implementation
- `app/decision_provider.py` contains `Decision`, `DecisionProvider`, `JEVDecisionProvider`, and `build_decision_input`.
- JEV SDK request/response format is **not verified**. The adapter raises `NotImplementedError` rather than fabricate a response.
- Do not interpret vector distance as a calibrated probability.
- Do not allow provider results to bypass validation, approval, authorization or tenant isolation.

## Completion criteria
- Verify the installed SDK and its `system_one` / `Choice` / `Score` / `Noul` signatures against official documentation.
- Implement strict output parsing with candidate allowlisting and finite [0,1] scores where appropriate.
- Add timeout, rate limiting, audit metadata, provider/model version, and fail-closed fallback.
- Connect the adapter to the discovery-time RAG pipeline, never the per-event executor.
- Add integration tests before enabling in production.
