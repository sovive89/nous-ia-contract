# OpenAI Contract Review Agent

Module: `app/contract_review_agent.py`.

Install `openai` and `pydantic>=2`; configure `OPENAI_API_KEY` on the server. Inject an `OpenAI()` client into `OpenAIContractReviewAgent` and call `review(source, proposed_decision, evidence)`.

The agent returns a structured verdict (`approvable`, `needs_review`, `reject_recommended`), rationale, findings with known evidence IDs and `requires_human_review=true`. Evidence must be tenant-scoped and sanitized. Never send raw payloads, credentials or sensitive data.

An `approvable` verdict is advisory, not authorization. Deterministic validation, human approval, contract versioning and audit are separate mandatory stages.

Pending: wire to authenticated discovery workflow and audit registry; verify live OpenAI API/model behavior; configure timeouts, retries, cost controls and version pinning; write and execute tests. Tests were not run.