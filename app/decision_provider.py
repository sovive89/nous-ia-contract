"""JEV discovery-time decision adapter. Never approves or activates contracts."""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any, Protocol

@dataclass(frozen=True)
class Decision:
    candidate_id: str | None
    risk_score: float | None
    equivalence_probability: float | None
    provider: str
    requires_review: bool = True

class DecisionProvider(Protocol):
    def evaluate(self, source: dict[str, Any], candidates: list[dict[str, Any]]) -> Decision: ...

def _prob(value: Any) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("invalid probability")
    return value

class JEVDecisionProvider:
    """Inject TypeSafeClient; caller owns client lifetime and credentials."""
    def __init__(self, client: Any, model: str = "jev-latest"):
        self.client = client
        self.model = model

    def evaluate(self, source: dict[str, Any], candidates: list[dict[str, Any]]) -> Decision:
        if not candidates:
            return Decision(None, None, None, "jev", True)
        if len(candidates) > 20:
            raise ValueError("too many candidates")
        ids = [str(c["evidence_id"]) for c in candidates]
        if len(ids) != len(set(ids)) or not all(ids):
            raise ValueError("candidate IDs must be unique and nonempty")
        from typesafe_sdk import Choice, Noul, Score

        labels = {f"candidate_{i}": str(c.get("description", ""))[:1200]
                  for i, c in enumerate(candidates)}
        labels["none"] = "No candidate is semantically equivalent; evidence is insufficient."
        state = {
            "source": {k: source.get(k) for k in ("system", "path", "field_type", "description")},
            "candidates": [
                {"label": f"candidate_{i}", "system": c.get("system"),
                 "path": c.get("path"), "description": str(c.get("description", ""))[:1200]}
                for i, c in enumerate(candidates)
            ],
            "instruction": "Only use supplied evidence. Similarity does not prove equivalence.",
        }
        response = self.client.system_one(
            state=state,
            questions={
                "mapping": Choice(instructions="Select best equivalent field, or none.", criteria=labels),
                "risk": Score(
                    instructions="Risk of incompatible field semantics, units or transformations.",
                    criteria=["No apparent mismatch", "Low", "Moderate", "High", "Critical"],
                ),
                "equivalent": Noul(
                    instructions="Does the selected candidate have equivalent business meaning to the source, based solely on supplied evidence?"
                ),
            },
            model=self.model,
        )
        selected = response.choices["mapping"].choice
        if selected not in labels:
            raise ValueError("JEV returned unknown candidate")
        risk = float(response.scores["risk"].score)
        if not math.isfinite(risk) or not 0 <= risk <= 4:
            raise ValueError("invalid JEV risk score")
        probability = _prob(response.nouls["equivalent"].noul)
        _prob(response.choices["mapping"].confidence)
        return Decision(
            None if selected == "none" else ids[int(selected.split("_")[1])],
            risk, probability, "jev", True,
        )

def build_decision_input(source: dict[str, Any], matches: list[Any]) -> list[dict[str, Any]]:
    return [
        {"evidence_id": str(m.evidence_id), "system": m.system,
         "path": m.path, "description": m.text, "distance": float(m.distance)}
        for m in matches
    ]
