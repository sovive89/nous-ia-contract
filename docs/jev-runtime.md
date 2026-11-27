# JEV runtime adapter

SDK documentation: https://typesafe-jev.com/en/guides/python/

Install `typesafe-sdk==0.7.5` in a Python >=3.10 environment, configure `TYPESAFE_API_KEY` on the server, and instantiate `TypeSafeClient`. Inject it into `JEVDecisionProvider`:

```python
from typesafe_sdk import TypeSafeClient
from app.decision_provider import JEVDecisionProvider

with TypeSafeClient() as client:
    provider = JEVDecisionProvider(client, model="jev-latest")
    decision = provider.evaluate(source, candidates)
```

`source` should include system, path, field_type and description. `candidates` is a list of RAG evidence records with evidence_id, system, path and description.

The adapter calls one `system_one` with Choice, Score, Noul and always marks output `requires_review=True`. Risk is on a 0-4 ordinal scale, not a calibrated probability. Noul returns a 0-1 probability-like estimate; neither metric can authorize a mapping.

**Not yet done:** connect to API route/discovery workflow, pin validated model version, run tests, verify real authenticated response, capture request IDs and usage in audit, implement timeout/retry policy and enforce tenant authorization at the caller boundary. Never send raw payload values or secrets to JEV. The executor remains deterministic.
